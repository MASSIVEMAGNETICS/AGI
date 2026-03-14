import hashlib
from typing import Any, Dict


async def generate_pdf(template: Dict[str, Any], variables: Dict[str, Any]) -> str:
    """
    Generate PDF from template and variables

    This is a simplified implementation for MVP.
    In production, this would use WeasyPrint or Puppeteer for high-fidelity rendering.
    """
    # TODO: Implement actual PDF generation
    # For now, return a placeholder URL

    template_id = template.get("id", "unknown")
    content_hash = hashlib.sha256(str(variables).encode()).hexdigest()[:8]

    pdf_url = f"https://storage.docushop.example/pdfs/{template_id}-{content_hash}.pdf"

    return pdf_url


async def generate_html_from_template(
    template: Dict[str, Any], variables: Dict[str, Any]
) -> str:
    """
    Generate HTML from template by replacing variables
    """
    html_parts = ['<!DOCTYPE html><html><head><meta charset="UTF-8">']
    html_parts.append("<style>")
    html_parts.append(
        "body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }"
    )
    html_parts.append(
        ".page { width: 8.5in; min-height: 11in; padding: 0.5in; box-sizing: border-box; }"
    )
    html_parts.append(".element { position: absolute; }")
    html_parts.append("</style>")
    html_parts.append("</head><body>")

    for page in template.get("pages", []):
        html_parts.append('<div class="page">')

        for element in page.get("elements", []):
            x = element.get("x", 0)
            y = element.get("y", 0)
            w = element.get("w", 100)
            h = element.get("h", 20)

            style = f"left:{x}px; top:{y}px; width:{w}px; height:{h}px;"

            if element.get("type") == "text" or element.get("type") == "richtext":
                text = element.get("props", {}).get("text", "")
                # Replace variables
                for var_name, var_value in variables.items():
                    text = text.replace(f"{{{{{var_name}}}}}", str(var_value))

                html_parts.append(f'<div class="element" style="{style}">{text}</div>')

            elif element.get("type") == "image":
                src = element.get("props", {}).get("src", "")
                html_parts.append(
                    f'<img class="element" style="{style}" src="{src}" />'
                )

        html_parts.append("</div>")

    html_parts.append("</body></html>")

    return "".join(html_parts)
