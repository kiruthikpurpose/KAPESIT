# Contributing to KAPESIT

Thank you for your interest in contributing to **KAPESIT**! Whether you're fixing a bug, adding a feature, or improving documentation, your contributions are highly valued. This guide will help you get started with the contribution process.

## How Can You Contribute?

There are several ways you can contribute to **KAPESIT**:

- **Reporting Bugs**: If you encounter any issues while using the project, let me know by opening a bug report.
- **Suggesting Enhancements**: Have an idea for a new feature or improvement? Open an enhancement issue to discuss your thoughts.
- **Improving Documentation**: Help improve the documentation by fixing typos, clarifying explanations, or adding examples.
- **Writing Code**: If you're a developer, contribute by fixing issues, adding new features, or improving the existing code.
- **Optimizing Simulations**: If you have experience with robotic simulations or machine learning models, help optimize the simulations for better performance or accuracy.

## Contribution Process

1. **Fork the Repository**: Start by forking the repository to your GitHub account.
   
2. **Clone Your Fork**:
   ```bash
   git clone https://github.com/kiruthikpurpose/KAPESIT.git
   ```

3. **Create a Branch**:
   Create a new branch for your contribution to ensure your work is isolated:
   ```bash
   git checkout -b feature-or-bug-description
   ```

4. **Make Changes**:
   - If you're working on code, write clean, maintainable, and well-commented code.
   - Make sure your changes follow the project's coding standards and guidelines.
   - If you're adding a new feature, ensure it's properly documented.
   - If you're fixing a bug, add a test case to verify the fix.

5. **Run Tests**:
   Before submitting your contribution, run all tests to ensure that nothing is broken.
   - For neural network-related contributions, use the test scripts provided in the repository.
   - If you're contributing to simulations, make sure to run tests in the simulation environment (Gazebo/Webots).

6. **Commit Your Changes**:
   Write clear, descriptive commit messages:
   ```bash
   git commit -m "Add detailed description of your changes"
   ```

7. **Push to Your Fork**:
   ```bash
   git push origin feature-or-bug-description
   ```

8. **Submit a Pull Request**:
   - Go to the original repository on GitHub and submit a Pull Request (PR) from your fork.
   - Include a detailed description of the changes you made and the purpose behind them.
   - If applicable, include screenshots or logs of your tests.
   - Link the pull request to the relevant issue (if applicable) to provide context.

## Code Guidelines

To maintain the quality and readability of the project, please adhere to the following guidelines when contributing code:

### 1. **Style Guidelines**:
   - Use consistent indentation (4 spaces for Python code).
   - Follow PEP 8 standards for Python.
   - Ensure proper naming conventions for functions, variables, and files.
   - Use descriptive variable and function names that clearly communicate their purpose.

### 2. **Commenting**:
   - Comment on your code where necessary, especially in complex sections.
   - Write docstrings for all functions and classes. Example:
     ```python
     def predict_dip(input_data):
         """
         Predicts dips in the robot's movement trajectory using trained neural networks.
         
         Args:
             input_data (numpy array): Input data representing the robot's current movement.
         
         Returns:
             bool: True if a dip is predicted, False otherwise.
         """
         pass
     ```

### 3. **Testing**:
   - Make sure to write unit tests for any new functionality.
   - Test code should be located in the `tests/` folder, and should be executable using a command like:
     ```bash
     python -m unittest discover -s tests
     ```
   - If you modify the neural network, ensure the model is validated through test scripts provided in the project.

### 4. **Documentation**:
   - Any changes to the code that affect the functionality should be reflected in the relevant documentation.
   - Ensure that the documentation is clear, concise, and updated as per your contributions.

## Issues and Bug Reports

If you encounter a bug or would like to request a new feature, follow these steps:

1. **Search Existing Issues**: First, check if there is already an open issue related to your problem or idea.
2. **Create a New Issue**: If no existing issue is found, open a new one and provide detailed information, including:
   - A clear description of the bug or feature request.
   - Steps to reproduce the issue, if applicable.
   - Screenshots, logs, or relevant error messages to illustrate the problem.
3. **Label Your Issue**: Use relevant labels such as `bug`, `enhancement`, `documentation`, etc., to categorize the issue.

## Code of Conduct

This project adheres to an open, collaborative, and respectful environment. By participating, you agree to uphold the following values:

- Be respectful and professional in your interactions.
- Provide constructive feedback and suggestions.
- Avoid any form of harassment, personal attacks, or inappropriate behavior.

For further details, refer to the [Code of Conduct](CODE_OF_CONDUCT.md) file.

## Additional Resources

Here are a few additional resources to help you get started:

- **GitHub Help**: If you're new to GitHub, check out [GitHub's documentation](https://docs.github.com/en) on how to fork a repo, submit pull requests, etc.
- **Gazebo/Webots Documentation**: Review the official documentation for these simulators to understand how to simulate environments for KAPESIT.
- **Machine Learning Resources**: Check out [TensorFlow](https://www.tensorflow.org/) and [PyTorch](https://pytorch.org/) documentation for more on building neural networks.

## Thank You!

Thank you again for your interest in contributing to **KAPESIT**! Every contribution, no matter how big or small, helps improve the project. I look forward to your ideas, improvements, and collaboration.

If you have any questions or need help, feel free to reach out by opening an issue or contacting me directly.
