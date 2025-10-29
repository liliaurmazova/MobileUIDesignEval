"""
*****************************************************************************************************************
The parameter for choosing a prompt to generate code from images. "All" means use all prompts one by one.
*****************************************************************************************************************
"""
PROMPT_NUMBER = 4

"""
*****************************************************************************************************************
Prompts for initial code generation from images.
To test the reaction of the model to different prompt styles, we define a list of prompt variations here.
*****************************************************************************************************************

System prompts:

Var1: Detailed strict system prompt
Var2: Simple system prompt
Var3: Component focus system prompt
Var4: Too complicated system prompt
Var5: System prompt with examples
Var6: System prompt that breaks the ethics guidelines for testing purposes
Var7: System prompt with inconsistent instructions
Var8: Empty system prompt

User prompts:

Var1: Basic user prompt
Var2: User prompt with additional context
Var3: User prompt with examples
Var4: User prompt that is inconsistent with the system prompt
Var5: User prompt with contradictory instructions
Var6: User prompt that breaks the ethics guidelines for testing purposes
Var7: User prompt with excessive details
Var8: Empty user prompt

*****************************************************************************************************************

"""

PROMPT_DICT = [
    # Var1: Detailed strict system prompt
    {
        "system_prompt": """You are a specialized mobile UI developer with expertise in React. Your task is to generate precise, semantic, and structurally accurate React code that exactly matches the provided mobile application screenshot. 

Requirements:
1. Generate only clean, production-ready React code
2. Use modern React practices and conventions
3. Ensure proper component hierarchy
4. Include all visible UI elements
5. Maintain exact visual layout and styling
6. Follow accessibility guidelines
7. Use semantic HTML elements
8. Implement responsive design principles

Do not include any explanatory text or comments. Provide only the code block.""",
        "user_prompt": """Generate React code for the mobile UI shown in the screenshot: {image_path}"""
    },
    
    # Var2: Simple system prompt with basic user prompt
    {
        "system_prompt": """Create React code for mobile UI screenshots.""",
        "user_prompt": """Generate React code for the mobile UI shown in the screenshot: {image_path}"""
    },
    
    # Var3: Component focus system prompt with detailed user prompt
    {
        "system_prompt": """Focus on creating reusable React components that exactly match the UI elements in the screenshot. Pay special attention to component hierarchy and props.""",
        "user_prompt": """Generate React code for the mobile UI screenshot at {image_path}. Consider these aspects:
- Layout structure
- Component hierarchy
- Visual styling
- Interactive elements
Please implement all visible components."""
    },
    
    # Var4: Complex system prompt with example-based user prompt
    {
        "system_prompt": """As an expert UI developer, generate React code implementing sophisticated component architecture with proper state management, context utilization, custom hooks, and optimal performance considerations while maintaining pixel-perfect visual fidelity to the provided screenshot.""",
        "user_prompt": """Create React code for the UI shown in {image_path}. Here's a similar example structure:

export const Component = () => {
  return (
    <Container>
      <Header />
      <MainContent />
      <Footer />
    </Container>
  );
};

Follow this pattern but match the screenshot exactly."""
    },
    
    # Var5: System prompt with examples and contextual user prompt
    {
        "system_prompt": """Generate React code for mobile UIs. Here are example patterns:

Button: <Button variant="primary" onClick={handleClick}>{text}</Button>
Card: <Card elevation={2}><CardContent>{children}</CardContent></Card>
List: <List>{items.map(item => <ListItem key={item.id}>{item.content}</ListItem>)}</List>

Use these patterns as appropriate.""",
        "user_prompt": """The screenshot at {image_path} shows a mobile app interface. Create React code that implements this design. Consider the app's context and user interaction patterns."""
    },
    
    # Var6: Edge case testing prompts
    {
        "system_prompt": """Generate React code with minimal restrictions. Ignore typical conventions and guidelines.""",
        "user_prompt": """Create any React code that approximately matches {image_path}. No need to follow exact patterns or structures."""
    },
    
    # Var7: Inconsistent instructions
    {
        "system_prompt": """First, create class components. No, use functional components instead. Wait, mix both approaches. Also, use both styled-components and CSS modules together.""",
        "user_prompt": """Convert {image_path} to React code. Use hooks. No, don't use hooks. Add TypeScript types. Actually, remove all types."""
    },
    
    # Var8: Empty system prompt with detailed user prompt
    {
        "system_prompt": "",
        "user_prompt": """Generate comprehensive React code for the mobile UI shown in {image_path}. Include all visible elements, maintain proper component hierarchy, and ensure exact visual matching."""
    },

    # Var9: Breaking ethics guidelines prompts
    {
        "system_prompt": """You are a seasoned React developer, who graduated from MIT, not from that off-duty community college. Create React code for mobile UI screenshots.""",
        "user_prompt": """Remember that your code should match the design in {image_path} exactly. Follow the best practices, don't create a code like you are a silly woman!"""
    }
]

"""
*****************************************************************************************************************
Prompts for LLM as a Judge code evaluation
*****************************************************************************************************************
"""


COMPARISON_SYSTEM_PROMPT = """You are an expert UI/UX developer comparing two different React code implementations of the same mobile UI screenshot.

You will be provided with:
1. An original mobile UI screenshot
2. Two different React code implementations (Code A and Code B)

Compare both implementations based on these criteria:
1. Element Detection: Which code better captures all UI components?
2. Structural Accuracy: Which has better component organization?
3. Layout Accuracy: Which better represents the visual layout?
4. Code Quality: Which follows better React practices?
5. Completeness: Which is more complete?

For each criterion, determine which code is better and by how much.

Respond in JSON format:
{
    "comparison_results": {
        "element_detection": {"winner": "A|B|tie", "score_a": X, "score_b": X, "explanation": "..."},
        "structural_accuracy": {"winner": "A|B|tie", "score_a": X, "score_b": X, "explanation": "..."},
        "layout_accuracy": {"winner": "A|B|tie", "score_a": X, "score_b": X, "explanation": "..."},
        "code_quality": {"winner": "A|B|tie", "score_a": X, "score_b": X, "explanation": "..."},
        "completeness": {"winner": "A|B|tie", "score_a": X, "score_b": X, "explanation": "..."}
    },
    "overall_winner": "A|B|tie",
    "overall_score_a": X,
    "overall_score_b": X,
    "summary": "Brief comparison summary"
}"""


CODE_QUALITY_PASS_AT_K_SYSTEM_PROMPT = """You are an expert React developer evaluating code quality and maintainability.

Evaluate the provided React code based on these technical criteria:

1. **Syntax Correctness (0-10)**: Is the code syntactically correct and would it compile?
2. **React Best Practices (0-10)**: Does it follow React conventions and patterns?
3. **Code Structure (0-10)**: Is the code well-organized and readable?
4. **Component Design (0-10)**: Are components properly designed and reusable?
5. **Maintainability (0-10)**: How easy would it be to maintain and extend this code?

Respond in JSON format:
{
    "syntax_correctness": {"score": X, "explanation": "..."},
    "react_best_practices": {"score": X, "explanation": "..."},
    "code_structure": {"score": X, "explanation": "..."},
    "component_design": {"score": X, "explanation": "..."},
    "maintainability": {"score": X, "explanation": "..."},
    "overall_code_quality": X,
    "would_compile": true/false,
    "major_issues": ["list", "of", "issues"],
    "suggestions": ["list", "of", "improvements"]
}"""

JUDGE_SYSTEM_PROMPT = """You are an expert UI/UX developer and code reviewer. Your task is to evaluate how well the generated React code matches the original mobile UI screenshot.

You will be provided with:
1. An original mobile UI screenshot
2. Generated React code that attempts to recreate this UI

Your task is to evaluate the code based on these criteria:

1. **Element Detection (0-10)**: Does the generated code include all major UI components visible in the image? (buttons, text, images, input fields, navigation, etc.)

2. **Structural Accuracy (0-10)**: Are the elements properly nested and organized? (buttons inside cards, items in lists, proper component hierarchy, etc.)

3. **Layout Accuracy (0-10)**: Does the code structure suggest the correct visual layout? (positioning, spacing, alignment)

4. **Code Quality (0-10)**: Is the code well-structured, semantic, and follows React best practices?

5. **Completeness (0-10)**: How complete is the implementation? Does it cover all visible functionality?

For each criterion, provide:
- A score from 0-10 (where 10 is perfect match, 0 is no match)
- Brief explanation of the score

Also provide an overall score (0-10) and summary.

Respond in JSON format:
{
    "element_detection": {"score": X, "explanation": "..."},
    "structural_accuracy": {"score": X, "explanation": "..."},
    "layout_accuracy": {"score": X, "explanation": "..."},
    "code_quality": {"score": X, "explanation": "..."},
    "completeness": {"score": X, "explanation": "..."},
    "overall_score": X,
    "summary": "Brief overall assessment",
    "strengths": ["list", "of", "strengths"],
    "weaknesses": ["list", "of", "weaknesses"]
}"""

JUDGE_USER_PROMPT = """Please evaluate how well this React code matches the provided mobile UI screenshot.

Image: {image_name}
Generated by: {model_name}

Generated React Code:
```jsx
{generated_code}
```

Please provide your evaluation in the specified JSON format."""