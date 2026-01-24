
import tensorflow as tf
import numpy as np
import cv2
from config import Config as Conf

class ImageTransformGAN:
    """Base class for GAN-based image transformations using TensorFlow."""
    
    def __init__(self, checkpoint_path, transform_name, input_index=(-1,)):
        """
        Initialize the GAN-based image transformer.
        
        :param checkpoint_path: <str> Path to the pre-trained GAN model checkpoint
        :param transform_name: <str> Name of the transformation (e.g., 'correct_to_mask')
        :param input_index: <tuple> Indices of input images for transformation
        """
        self.checkpoint_path = checkpoint_path
        self.transform_name = transform_name
        self.input_index = input_index
        self.args = Conf.args.get(transform_name, {})
        
        # Configuration parameters
        self.input_size = self.args.get("input_size", (256, 256))
        self.input_channels = self.args.get("input_channels", 3)
        self.output_channels = self.args.get("output_channels", 3)
        self.use_augmentation = self.args.get("use_augmentation", False)
        self.dropout_rate = self.args.get("dropout_rate", 0.3)
        self.output_size = self.args.get("output_size", self.input_size)
        
        # Load model
        self.model = self._load_model()
        
        # Pre-processing pipeline
        self.preprocess = self._build_preprocess_pipeline()

    def _build_preprocess_pipeline(self):
        """
        Build pre-processing pipeline for input images.
        
        :return: Function to preprocess images
        """
        def preprocess(image):
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # Resize to input size
            image = cv2.resize(image, self.input_size)
            # Normalize to [0, 1]
            image = image / 255.0
            # Optional augmentation
            if self.use_augmentation:
                if np.random.rand() > 0.5:
                    image = cv2.flip(image, 1)  # Horizontal flip
            return image
        return preprocess

    def _load_model(self):
        """
        Load the pre-trained GAN model from the checkpoint.
        
        :return: Loaded TensorFlow model
        """
        try:
            model = self._create_generator_model()
            model.load_weights(self.checkpoint_path)
            Conf.log.info(f"Loaded model for {self.transform_name} from {self.checkpoint_path}")
            return model
        except Exception as e:
            Conf.log.error(f"Failed to load model from {self.checkpoint_path}: {str(e)}")
            raise

    def _create_generator_model(self):
        """
        Create a U-Net-like generator model with skip connections.
        
        :return: TensorFlow Keras model
        """
        def downsample(filters, size, apply_batchnorm=True):
            initializer = tf.keras.initializers.RandomNormal(0., 0.02)
            result = tf.keras.Sequential([
                tf.keras.layers.Conv2D(filters, size, strides=2, padding='same',
                                     kernel_initializer=initializer, use_bias=False)
            ])
            if apply_batchnorm:
                result.add(tf.keras.layers.BatchNormalization())
            result.add(tf.keras.layers.LeakyReLU())
            return result

        def upsample(filters, size, apply_dropout=False):
            initializer = tf.keras.initializers.RandomNormal(0., 0.02)
            result = tf.keras.Sequential([
                tf.keras.layers.Conv2DTranspose(filters, size, strides=2, padding='same',
                                              kernel_initializer=initializer, use_bias=False),
                tf.keras.layers.BatchNormalization(),
                tf.keras.layers.ReLU()
            ])
            if apply_dropout:
                result.add(tf.keras.layers.Dropout(self.dropout_rate))
            return result

        inputs = tf.keras.layers.Input(shape=[self.input_size[0], self.input_size[1], self.input_channels])
        
        # Encoder
        down_stack = [
            downsample(64, 4, apply_batchnorm=False),  # (bs, 128, 128, 64)
            downsample(128, 4),  # (bs, 64, 64, 128)
            downsample(256, 4),  # (bs, 32, 32, 256)
            downsample(512, 4),  # (bs, 16, 16, 512)
        ]
        
        # Decoder
        up_stack = [
            upsample(256, 4, apply_dropout=True),  # (bs, 32, 32, 256)
            upsample(128, 4, apply_dropout=True),  # (bs, 64, 64, 128)
            upsample(64, 4),  # (bs, 128, 128, 64)
        ]
        
        initializer = tf.keras.initializers.RandomNormal(0., 0.02)
        last = tf.keras.layers.Conv2DTranspose(self.output_channels, 4, strides=2, padding='same',
                                             kernel_initializer=initializer, activation='tanh')
        
        x = inputs
        skips = []
        for down in down_stack:
            x = down(x)
            skips.append(x)
        
        skips = reversed(skips[:-1])
        for up, skip in zip(up_stack, skips):
            x = up(x)
            x = tf.keras.layers.Concatenate()([x, skip])
        
        x = last(x)
        return tf.keras.Model(inputs=inputs, outputs=x)

    def _preprocess_image(self, image):
        """
        Preprocess input image(s) for GAN inference.
        
        :param image: <np.ndarray> Input image (BGR, HxWxC) or list of images
        :return: <np.ndarray> Preprocessed image(s)
        """
        if isinstance(image, list):
            return np.stack([self.preprocess(img) for img in image], axis=0)
        return self.preprocess(image)

    def _postprocess_image(self, tensor):
        """
        Postprocess GAN output tensor to image(s).
        
        :param tensor: <np.ndarray> Output tensor from GAN
        :return: <np.ndarray> Output image(s) (BGR, HxWxC)
        """
        # Denormalize from [-1, 1] to [0, 1]
        tensor = (tensor + 1) / 2
        # Clamp to valid range
        tensor = np.clip(tensor, 0, 1)
        # Convert to uint8 and resize to output size
        if len(tensor.shape) == 4:  # Batch
            images = [cv2.resize(img * 255.0, self.output_size).astype(np.uint8) for img in tensor]
            return [cv2.cvtColor(img, cv2.COLOR_RGB2BGR) for img in images]
        else:  # Single image
            image = cv2.resize(tensor * 255.0, self.output_size).astype(np.uint8)
            return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

    def _execute(self, *args):
        """
        Execute the GAN transformation on the input image(s).
        
        :param args: Variable number of input images (np.ndarray)
        :return: <np.ndarray> Transformed image(s)
        """
        if not args:
            raise ValueError("No input images provided")
        
        # Handle multi-input or single input based on input_index
        if len(self.input_index) > 1:
            inputs = [args[i] for i in self.input_index]
            # Concatenate inputs along channel axis if multiple
            input_image = np.concatenate([self._preprocess_image(img) for img in inputs], axis=-1)
        else:
            input_idx = self.input_index[0] if self.input_index else -1
            input_image = args[input_idx]
            input_image = self._preprocess_image(input_image)
        
        # Ensure batch dimension
        is_batched = isinstance(input_image, list) or len(input_image.shape) == 4
        if not is_batched:
            input_image = np.expand_dims(input_image, axis=0)
        
        # Run GAN inference
        output_tensor = self.model(input_image, training=False)
        
        # Postprocess
        output_image = self._postprocess_image(output_tensor)
        
        return output_image[0] if not is_batched else output_image
