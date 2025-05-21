# Ollama Model Evaluation Criteria for Victor

## Overview
This document outlines the process and criteria for evaluating different Ollama-compatible models to select the best option for the Victor AI coding assistant.

## Evaluation Criteria

### Core Capabilities
1. **Lua Language Understanding**
   - Comprehension of Lua syntax and semantics
   - Understanding of Lua idioms and best practices
   - Recognition of DCS-specific Lua patterns and APIs

2. **Code Analysis Abilities**
   - Quality of code explanation
   - Ability to trace execution flow
   - Understanding of dependencies between files

3. **Performance Metrics**
   - Response time on Mac Mini hardware
   - Memory usage during operation
   - Token efficiency (quality of response per token)

### Practical Requirements
1. **Model Size Constraints**
   - Must run efficiently on Mac Mini hardware
   - Balance between model size and performance

2. **Context Window**
   - Sufficient context window to understand related code
   - Ability to process larger files when needed

3. **Fine-tuning Potential**
   - Adaptability to DCS-specific domain knowledge
   - Options for further specialization

## Candidate Models
Initial models to evaluate:

1. **CodeLlama Family**
   - CodeLlama 7B, 13B, 34B
   - Specialized for code understanding

2. **Llama3 Family**
   - Llama3 8B, 70B
   - Strong general reasoning with good code capabilities

3. **Mistral Family**
   - Mistral 7B, Mixtral 8x7B
   - Strong performance-to-size ratio

4. **Specialized Code Models**
   - StarCoder2
   - DeepSeek Coder
   - WizardCoder

## Evaluation Process
1. **Benchmark Creation**
   - Develop benchmark test set from actual XSAF codebase
   - Include representative examples of common tasks

2. **Testing Methodology**
   - Standardized prompts for each test case
   - Blind evaluation of responses

3. **Scoring System**
   - Correctness (1-5)
   - Completeness (1-5)
   - Clarity (1-5)
   - Performance metrics (response time, memory usage)

4. **Final Selection**
   - Calculate weighted scores based on project priorities
   - Consider practical requirements and constraints
   - Document strengths and weaknesses of top candidates

## Timeline
- Model identification and setup: 1 week
- Benchmark creation: 1 week
- Evaluation process: 2 weeks
- Final selection and documentation: 1 week