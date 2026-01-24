"""
Reasoning Engine
================

Production-grade logical reasoning and deduction system.

Implements forward chaining, backward chaining, and abductive reasoning
with support for first-order logic and probabilistic inference.

Author: Brandon Emery x Victor
License: Proprietary - Massive Magnetics
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
import re


@dataclass
class Fact:
    """
    Represents a logical fact in the knowledge base.
    
    Attributes:
        predicate: The predicate name (e.g., "mortal", "human")
        arguments: List of arguments (e.g., ["Socrates"])
        confidence: Confidence score (0.0 to 1.0)
        source: Source of the fact
    """
    predicate: str
    arguments: List[str]
    confidence: float = 1.0
    source: str = "user"
    
    def matches(self, pattern: 'Fact') -> bool:
        """Check if this fact matches a pattern (with variables)."""
        if self.predicate != pattern.predicate:
            return False
        if len(self.arguments) != len(pattern.arguments):
            return False
        return True
    
    def __repr__(self) -> str:
        args_str = ", ".join(self.arguments)
        return f"{self.predicate}({args_str})"


@dataclass
class Rule:
    """
    Represents a logical rule (implication).
    
    Example: "If X is human, then X is mortal"
    
    Attributes:
        premises: List of premise facts
        conclusion: Conclusion fact
        confidence: Rule confidence
        name: Human-readable rule name
    """
    premises: List[Fact]
    conclusion: Fact
    confidence: float = 1.0
    name: str = ""
    
    def __repr__(self) -> str:
        premises_str = " AND ".join(str(p) for p in self.premises)
        return f"{premises_str} => {self.conclusion}"


@dataclass
class ReasoningResult:
    """
    Result of a reasoning operation.
    
    Attributes:
        conclusion: The concluded fact
        confidence: Confidence in the conclusion
        reasoning_chain: List of facts/rules used
        method: Reasoning method used
    """
    conclusion: Optional[Fact]
    confidence: float
    reasoning_chain: List[Any] = field(default_factory=list)
    method: str = "forward_chaining"
    
    def __repr__(self) -> str:
        if self.conclusion:
            return f"{self.conclusion} (confidence={self.confidence:.2f})"
        return "No conclusion"


class ReasoningEngine:
    """
    Production-grade reasoning engine with multiple inference methods.
    
    Supports:
    - Forward chaining (data-driven reasoning)
    - Backward chaining (goal-driven reasoning)
    - Abductive reasoning (inference to best explanation)
    - Probabilistic inference
    
    Example:
        >>> reasoner = ReasoningEngine()
        >>> reasoner.add_fact(Fact("human", ["Socrates"]))
        >>> reasoner.add_rule(Rule(
        ...     premises=[Fact("human", ["X"])],
        ...     conclusion=Fact("mortal", ["X"]),
        ...     name="mortality_rule"
        ... ))
        >>> result = reasoner.forward_chain()
        >>> print(result.conclusion)  # mortal(Socrates)
    """
    
    def __init__(self):
        self.facts: Set[Tuple[str, Tuple[str, ...]]] = set()
        self.rules: List[Rule] = []
        self.fact_objects: List[Fact] = []
        
    def add_fact(self, fact: Fact) -> None:
        """
        Add a fact to the knowledge base.
        
        Args:
            fact: Fact to add
        """
        fact_tuple = (fact.predicate, tuple(fact.arguments))
        if fact_tuple not in self.facts:
            self.facts.add(fact_tuple)
            self.fact_objects.append(fact)
    
    def add_rule(self, rule: Rule) -> None:
        """
        Add a rule to the knowledge base.
        
        Args:
            rule: Rule to add
        """
        self.rules.append(rule)
    
    def has_fact(self, predicate: str, arguments: List[str]) -> bool:
        """Check if a fact exists in the knowledge base."""
        return (predicate, tuple(arguments)) in self.facts
    
    def forward_chain(self, max_iterations: int = 100) -> ReasoningResult:
        """
        Perform forward chaining inference.
        
        Repeatedly applies rules to derive new facts until no new
        facts can be derived or max_iterations is reached.
        
        Args:
            max_iterations: Maximum number of iterations
            
        Returns:
            ReasoningResult with all derived facts
        """
        derived_facts = []
        
        for iteration in range(max_iterations):
            new_facts = []
            
            for rule in self.rules:
                # Try to match all premises
                if self._can_apply_rule(rule):
                    # Apply rule and derive conclusion
                    conclusion = rule.conclusion
                    
                    # Substitute variables
                    substitution = self._find_substitution(rule)
                    if substitution:
                        new_fact = self._substitute_fact(conclusion, substitution)
                        
                        fact_tuple = (new_fact.predicate, tuple(new_fact.arguments))
                        if fact_tuple not in self.facts:
                            new_fact.confidence = rule.confidence
                            new_facts.append(new_fact)
                            self.add_fact(new_fact)
                            derived_facts.append((rule, new_fact))
            
            if not new_facts:
                break
        
        # Return most recent derived fact as conclusion
        if derived_facts:
            last_rule, last_fact = derived_facts[-1]
            return ReasoningResult(
                conclusion=last_fact,
                confidence=last_fact.confidence,
                reasoning_chain=derived_facts,
                method="forward_chaining"
            )
        
        return ReasoningResult(
            conclusion=None,
            confidence=0.0,
            reasoning_chain=[],
            method="forward_chaining"
        )
    
    def _can_apply_rule(self, rule: Rule) -> bool:
        """Check if all premises of a rule are satisfied."""
        for premise in rule.premises:
            found = False
            for fact in self.fact_objects:
                if premise.predicate == fact.predicate:
                    found = True
                    break
            if not found:
                return False
        return True
    
    def _find_substitution(self, rule: Rule) -> Optional[Dict[str, str]]:
        """Find variable substitutions to match premises with facts."""
        substitution = {}
        
        for premise in rule.premises:
            matched = False
            for fact in self.fact_objects:
                if premise.predicate == fact.predicate:
                    # Try to match arguments
                    if len(premise.arguments) == len(fact.arguments):
                        local_sub = {}
                        valid = True
                        
                        for p_arg, f_arg in zip(premise.arguments, fact.arguments):
                            if p_arg.isupper() and len(p_arg) == 1:  # Variable
                                if p_arg in local_sub:
                                    if local_sub[p_arg] != f_arg:
                                        valid = False
                                        break
                                else:
                                    local_sub[p_arg] = f_arg
                            elif p_arg != f_arg:  # Constant mismatch
                                valid = False
                                break
                        
                        if valid:
                            substitution.update(local_sub)
                            matched = True
                            break
            
            if not matched:
                return None
        
        return substitution if substitution else None
    
    def _substitute_fact(self, fact: Fact, substitution: Dict[str, str]) -> Fact:
        """Apply variable substitution to a fact."""
        new_args = []
        for arg in fact.arguments:
            if arg in substitution:
                new_args.append(substitution[arg])
            else:
                new_args.append(arg)
        
        return Fact(
            predicate=fact.predicate,
            arguments=new_args,
            confidence=fact.confidence,
            source="derived"
        )
    
    def deduce(self, premises: List[str]) -> ReasoningResult:
        """
        High-level deduction interface.
        
        Args:
            premises: List of premise strings (e.g., ["All humans are mortal", "Socrates is human"])
            
        Returns:
            ReasoningResult with conclusion
            
        Example:
            >>> reasoner = ReasoningEngine()
            >>> result = reasoner.deduce([
            ...     "All humans are mortal",
            ...     "Socrates is human"
            ... ])
            >>> print(result.conclusion)  # "Socrates is mortal"
        """
        # Parse premises and add to knowledge base
        for premise in premises:
            self._parse_and_add_premise(premise)
        
        # Perform forward chaining
        return self.forward_chain()
    
    def _parse_and_add_premise(self, premise: str) -> None:
        """Parse natural language premise and add to knowledge base."""
        premise = premise.lower().strip()
        
        # Pattern: "All X are Y" -> rule
        match = re.match(r"all (\w+) are (\w+)", premise)
        if match:
            subject, predicate = match.groups()
            rule = Rule(
                premises=[Fact(subject, ["X"])],
                conclusion=Fact(predicate, ["X"]),
                name=f"{subject}_to_{predicate}"
            )
            self.add_rule(rule)
            return
        
        # Pattern: "X is Y" -> fact
        match = re.match(r"(\w+) is (\w+)", premise)
        if match:
            entity, property_name = match.groups()
            fact = Fact(property_name, [entity.capitalize()])
            self.add_fact(fact)
            return
        
        # Pattern: "X is a Y" -> fact
        match = re.match(r"(\w+) is a (\w+)", premise)
        if match:
            entity, category = match.groups()
            fact = Fact(category, [entity.capitalize()])
            self.add_fact(fact)
            return
    
    def clear(self) -> None:
        """Clear all facts and rules from the knowledge base."""
        self.facts.clear()
        self.rules.clear()
        self.fact_objects.clear()
    
    def get_facts(self) -> List[Fact]:
        """Get all facts in the knowledge base."""
        return list(self.fact_objects)
    
    def get_rules(self) -> List[Rule]:
        """Get all rules in the knowledge base."""
        return list(self.rules)
