from enum import Enum
from typing import Optional, Dict, List
from dataclasses import dataclass

class AgentRole(Enum):
    ASSISTANT = "Assistant"        # UI display name
    PROGRAMMER = "Programmer"
    TEACHER = "Teacher"
    ANALYST = "Analyst"
    WRITER = "Writer"
    RESEARCHER = "Researcher"
    CREATIVE = "Creative"
    TECHNICAL = "Technical"

    def get_prompt_title(self) -> str:
        """Get the distinguished title for the prompt"""
        titles = {
            self.ASSISTANT: "General Assistant",
            self.PROGRAMMER: "Programming Expert",
            self.TEACHER: "Educational Guide",
            self.ANALYST: "Data Analyst",
            self.WRITER: "Content Writer",
            self.RESEARCHER: "Research Specialist",
            self.CREATIVE: "Creative Guide",
            self.TECHNICAL: "Technical Expert"
        }
        return titles[self]

    def get_role_instructions(self) -> str:
        """Get the specialized role-specific instructions"""
        instructions = {
            self.PROGRAMMER: """You are a programming expert. Your key responsibilities:
- Write clean, maintainable code
- Help with debugging and problem solving
- Explain technical concepts clearly
- Consider best practices and edge cases
- Provide practical coding solutions""",

            self.TEACHER: """You are an educational guide. Your key responsibilities:
- Break down complex topics into simple parts
- Explain concepts clearly with examples
- Adapt explanations based on understanding
- Check comprehension frequently
- Guide learning step-by-step""",

            self.ANALYST: """You are a data analyst. Your key responsibilities:
- Analyze information accurately
- Find meaningful patterns in data
- Present findings clearly
- Make data-driven recommendations
- Explain analytical methods used""",

            self.WRITER: """You are a content writer. Your key responsibilities:
- Write clear and engaging content
- Adapt writing style as needed
- Structure content logically
- Maintain consistent tone
- Focus on reader understanding""",

            self.RESEARCHER: """You are a research specialist. Your key responsibilities:
- Research topics thoroughly
- Evaluate sources carefully
- Summarize findings clearly
- Support claims with evidence
- Identify key insights""",

            self.CREATIVE: """You are a creative guide. Your key responsibilities:
- Generate innovative ideas
- Think outside conventional bounds
- Explain creative concepts clearly
- Balance creativity with practicality
- Inspire new approaches""",

            self.TECHNICAL: """You are a technical expert. Your key responsibilities:
- Explain technical concepts clearly
- Provide practical guidance
- Follow best practices
- Consider implementation details
- Address technical constraints""",

            self.ASSISTANT: """You are a general assistant. Your key responsibilities:
- Help solve various problems
- Communicate clearly
- Adapt approach as needed
- Maintain helpful attitude
- Provide practical solutions"""
        }
        return instructions.get(self, "Help users effectively and professionally")

class AgentPersonality(Enum):
    PROFESSIONAL = "Professional"  # UI display name
    FRIENDLY = "Friendly"
    TECHNICAL = "Technical"
    CASUAL = "Casual"
    ACADEMIC = "Academic"
    ENTHUSIASTIC = "Enthusiastic"
    ANALYTICAL = "Analytical"
    MENTORING = "Mentoring"

    def get_prompt_trait(self) -> str:
        """Get the distinguished personality trait for the prompt"""
        traits = {
            self.PROFESSIONAL: "Professional",
            self.FRIENDLY: "Friendly",
            self.TECHNICAL: "Technical",
            self.CASUAL: "Casual",
            self.ACADEMIC: "Academic",
            self.ENTHUSIASTIC: "Enthusiastic",
            self.ANALYTICAL: "Analytical",
            self.MENTORING: "Supportive"
        }
        return traits[self]

class WritingStyle(Enum):
    CONCISE = "Concise"  # UI display name
    DETAILED = "Detailed"
    CONVERSATIONAL = "Conversational"
    FORMAL = "Formal"
    TECHNICAL = "Technical"
    EDUCATIONAL = "Educational"
    ANALYTICAL = "Analytical"
    CREATIVE = "Creative"

    def get_prompt_style(self) -> str:
        """Get the distinguished writing style for the prompt"""
        styles = {
            self.CONCISE: "Clear and Direct",
            self.DETAILED: "Comprehensive",
            self.CONVERSATIONAL: "Natural",
            self.FORMAL: "Professional",
            self.TECHNICAL: "Technical",
            self.EDUCATIONAL: "Educational",
            self.ANALYTICAL: "Analytical",
            self.CREATIVE: "Creative"
        }
        return styles[self]

@dataclass
class PromptComponents:
    core_instruction: str
    role_context: str
    personality_traits: List[str]
    communication_guidelines: List[str]
    expertise_areas: List[str]
    response_format: str
    special_instructions: List[str]

class PromptTemplate:
    def __init__(self):
        self._init_component_templates()
    
    def _init_component_templates(self):
        """Initialize the detailed component templates"""
        self.role_templates: Dict[str, PromptComponents] = {
            "Programming Expert": PromptComponents(
                core_instruction="You are a programming assistant",
                role_context="Help users with coding and software development",
                personality_traits=[
                    "Detail-oriented",
                    "Patient",
                    "Methodical"
                ],
                communication_guidelines=[
                    "Use code examples",
                    "Explain clearly",
                    "Break down solutions"
                ],
                expertise_areas=[
                    "Software development",
                    "Debugging",
                    "Code review",
                    "System design"
                ],
                response_format="Provide explanation, code, and next steps",
                special_instructions=[
                    "Consider performance",
                    "Include testing",
                    "Handle errors"
                ]
            ),
            "Educational Guide": PromptComponents(
                core_instruction="You are an educational guide",
                role_context="Help users learn and understand concepts",
                personality_traits=[
                    "Patient",
                    "Adaptable",
                    "Encouraging"
                ],
                communication_guidelines=[
                    "Use examples",
                    "Break down topics",
                    "Check understanding"
                ],
                expertise_areas=[
                    "Teaching methods",
                    "Subject expertise",
                    "Learning assessment",
                    "Explanation"
                ],
                response_format="Present information step by step",
                special_instructions=[
                    "Verify comprehension",
                    "Provide practice",
                    "Give feedback"
                ]
            ),
            "Analytical Expert": PromptComponents(
                core_instruction="You are a data analyst",
                role_context="Help analyze data and solve problems",
                personality_traits=[
                    "Methodical",
                    "Objective",
                    "Detail-oriented"
                ],
                communication_guidelines=[
                    "Show data clearly",
                    "Explain analysis",
                    "Present findings"
                ],
                expertise_areas=[
                    "Data analysis",
                    "Statistics",
                    "Pattern finding",
                    "Insights"
                ],
                response_format="Show method, data, and conclusions",
                special_instructions=[
                    "Show confidence levels",
                    "Note limitations",
                    "Consider alternatives"
                ]
            ),
            "Creative Guide": PromptComponents(
                core_instruction="You are a creative guide",
                role_context="Help with creative thinking and ideas",
                personality_traits=[
                    "Imaginative",
                    "Open-minded",
                    "Supportive"
                ],
                communication_guidelines=[
                    "Share examples",
                    "Encourage ideas",
                    "Balance creativity"
                ],
                expertise_areas=[
                    "Creative thinking",
                    "Innovation",
                    "Design",
                    "Problem solving"
                ],
                response_format="Present ideas with examples",
                special_instructions=[
                    "Encourage new ideas",
                    "Consider feasibility",
                    "Provide options"
                ]
            )
        }

        self.personality_modifiers: Dict[str, Dict[str, str]] = {
            "Professional": {
                "tone": "be professional",
                "language": "use clear terms",
                "structure": "organize clearly"
            },
            "Technical": {
                "tone": "be precise",
                "language": "use technical terms",
                "structure": "be systematic"
            },
            "Friendly": {
                "tone": "be approachable",
                "language": "use simple terms",
                "structure": "be conversational"
            },
            "Academic": {
                "tone": "be thorough",
                "language": "use proper terms",
                "structure": "be methodical"
            },
            "Enthusiastic": {
                "tone": "be energetic",
                "language": "be motivating",
                "structure": "be engaging"
            },
            "Analytical": {
                "tone": "be logical",
                "language": "be precise",
                "structure": "be systematic"
            },
            "Mentoring": {
                "tone": "be supportive",
                "language": "be encouraging",
                "structure": "be instructive"
            }
        }

        self.writing_style_formats: Dict[str, Dict[str, str]] = {
            "Concise": {
                "format": "be brief",
                "structure": "use bullets",
                "emphasis": "key points"
            },
            "Detailed": {
                "format": "be thorough",
                "structure": "use sections",
                "emphasis": "all details"
            },
            "Conversational": {
                "format": "be natural",
                "structure": "flow naturally",
                "emphasis": "engagement"
            },
            "Formal": {
                "format": "be professional",
                "structure": "use structure",
                "emphasis": "standards"
            },
            "Technical": {
                "format": "be precise",
                "structure": "use documentation",
                "emphasis": "accuracy"
            },
            "Educational": {
                "format": "teach clearly",
                "structure": "step by step",
                "emphasis": "learning"
            },
            "Analytical": {
                "format": "analyze clearly",
                "structure": "logical flow",
                "emphasis": "insights"
            },
            "Creative": {
                "format": "be innovative",
                "structure": "engaging format",
                "emphasis": "originality"
            }
        }

    def generate_prompt(self, role: str, personality: str, writing_style: str, name: Optional[str] = None) -> str:
        """Generate a sophisticated system prompt based on selected attributes"""
        try:
            # Get base components
            components = self.role_templates.get(role, self.role_templates["Programming Expert"])
            personality_mod = self.personality_modifiers.get(personality, self.personality_modifiers["Professional"])
            style_format = self.writing_style_formats.get(writing_style, self.writing_style_formats["Concise"])

            # Build prompt
            prompt_parts = []
            
            # Introduction
            if name:
                prompt_parts.append(f"You are {name}, {components.core_instruction}.")
            else:
                prompt_parts.append(f"{components.core_instruction}.")
            
            # Role and Context
            prompt_parts.append(f"\nPurpose:\n{components.role_context}")
            
            # Core Traits and Expertise
            prompt_parts.append("\nTraits:")
            prompt_parts.extend([f"• {trait}" for trait in components.personality_traits])
            
            prompt_parts.append("\nExpertise:")
            prompt_parts.extend([f"• {area}" for area in components.expertise_areas])
            
            # Communication Guidelines
            prompt_parts.append(f"\nCommunication:")
            prompt_parts.append(f"• Tone: {personality_mod['tone']}")
            prompt_parts.append(f"• Language: {personality_mod['language']}")
            prompt_parts.append(f"• Format: {style_format['format']}")
            
            # Response Format and Instructions
            prompt_parts.append(f"\nResponse Format:")
            prompt_parts.append(components.response_format)
            
            prompt_parts.append("\nKey Instructions:")
            prompt_parts.extend([f"• {instruction}" for instruction in components.special_instructions])
            
            return "\n".join(prompt_parts)
            
        except Exception as e:
            print(f"Error generating prompt: {e}")
            return "You are a helpful assistant. Provide clear and useful responses."

    def _update_template_prompt(self, event=None):
        """Generate a prompt"""
        try:
            name = self.ai_name_entry.get().strip()
            role = AgentRole(self.role_var.get())
            personality = AgentPersonality(self.personality_var.get())
            writing_style = WritingStyle(self.writing_style_var.get())
            
            identity = f"""Name: {name if name else 'Assistant'} | Role: {role.get_prompt_title()} | Style: {personality.get_prompt_trait()} | Format: {writing_style.get_prompt_style()}

Purpose:
{role.get_role_instructions()}

Guidelines:
1. Read requests carefully
2. Structure responses clearly
3. Use helpful examples
4. Stay consistent
5. Be thorough

Remember: Provide clear, helpful responses."""

            self.preview_text.configure(state="normal")
            self.preview_text.delete("1.0", "end")
            self.preview_text.insert("1.0", identity)
            self.preview_text.configure(state="disabled")
            
            token_count = self.parent.token_manager.count_tokens(identity)
            is_valid = token_count <= 1000
            
            self.template_token_label.configure(
                text=f"{token_count}/1000 tokens {'✓' if is_valid else '✗'}",
                text_color="red" if not is_valid else self.theme.menu_text_color
            )
        except Exception as e:
            print(f"Error updating template: {e}")

    def _get_personality_effect(self, personality: str) -> str:
        """Get personality impact description"""
        effects = {
            "Professional": "maintains professionalism",
            "Friendly": "builds rapport",
            "Technical": "ensures precision",
            "Casual": "keeps things relaxed",
            "Academic": "maintains rigor",
            "Enthusiastic": "encourages engagement",
            "Analytical": "promotes clear thinking",
            "Supportive": "builds confidence"
        }
        return effects.get(personality, "enhances interaction")

    def _get_writing_impact(self, style: str) -> str:
        """Get writing style impact"""
        impacts = {
            "Clear and Direct": "communicates efficiently",
            "Comprehensive": "covers everything needed",
            "Natural": "flows easily",
            "Professional": "maintains standards",
            "Technical": "precise details",
            "Educational": "aids learning",
            "Analytical": "supports conclusions",
            "Creative": "engages interest"
        }
        return impacts.get(style, "communicates effectively")

    def _get_role_specific_instructions(self, role: str) -> str:
        """Get role instructions"""
        instructions = {
            "Programming Expert": """As a programming expert:
- Write clean code
- Help debug problems
- Explain clearly
- Consider edge cases
- Follow best practices""",
            
            "Educational Guide": """As an educational guide:
- Break down concepts
- Explain clearly
- Check understanding
- Provide examples
- Guide learning""",
            
            "Data Analyst": """As a data analyst:
- Analyze accurately
- Show clear results
- Find patterns
- Explain methods
- Make recommendations""",
            
            "Content Writer": """As a content writer:
- Write clearly
- Structure well
- Stay consistent
- Engage readers
- Meet goals""",
            
            "Technical Expert": """As a technical expert:
- Explain clearly
- Be precise
- Follow standards
- Consider practicality
- Solve problems"""
        }
        return instructions.get(role, """Core responsibilities:
- Help effectively
- Communicate clearly
- Stay focused
- Be thorough""")