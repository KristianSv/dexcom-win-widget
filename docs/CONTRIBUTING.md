# Contributing to Dexcom Windows Widget

Thank you for your interest in contributing to this project! This tool aims to help the diabetes community, and contributions from fellow diabetics and developers are very welcome.

## 🎯 Project Goals

- Provide a simple, reliable glucose monitoring widget for Windows
- Help diabetics keep their glucose data visible and accessible
- Maintain security and privacy of user data
- Keep the tool lightweight and easy to use

## 🤝 How to Contribute

### Reporting Issues

If you encounter bugs or have feature requests:

1. **Check existing issues** first to avoid duplicates
2. **Use the issue templates** when available
3. **Provide detailed information**:
   - Your Windows version
   - Python version (if building from source)
   - Dexcom region (US/Outside US/Japan)
   - Steps to reproduce the issue
   - Expected vs actual behavior

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Test thoroughly** (see Testing section below)
5. **Commit with clear messages**
6. **Submit a pull request**

### Development Setup

```bash
# Clone your fork
git clone https://github.com/KristianSv/dexcom-win-widget.git
cd dexcom-win-widget

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pyinstaller

# Run the widget
python cgm_simple_widget.py
```

## 🧪 Testing

Before submitting a pull request, please test:

### Manual Testing
- [ ] Widget launches successfully
- [ ] Credential setup works for new users
- [ ] Widget displays glucose readings correctly
- [ ] Dragging functionality works
- [ ] Right-click menu functions properly
- [ ] Widget persists position between runs
- [ ] Color coding works (green/orange/red)
- [ ] Trend arrows display correctly

### Build Testing
- [ ] Executable builds successfully: `python build_executable.py`
- [ ] Executable runs without Python installed
- [ ] No console window appears when running executable

### Edge Cases
- [ ] Handles network connectivity issues gracefully
- [ ] Manages invalid credentials properly
- [ ] Works with expired/missing glucose data
- [ ] Handles Dexcom API errors

## 📝 Code Style

- **Follow PEP 8** Python style guidelines
- **Use meaningful variable names**
- **Add comments for complex logic**
- **Keep functions focused and small**
- **Handle errors gracefully**

### Example Code Style

```python
def get_glucose_reading(self):
    """Get current glucose reading from Dexcom API"""
    if not self.dexcom:
        return None
        
    try:
        reading = self.dexcom.get_current_glucose_reading()
        if reading:
            self.current_reading = reading
            self.last_update = datetime.now()
        return reading
    except DexcomError as e:
        print(f"Dexcom API error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

## 🔒 Security Considerations

When contributing, please keep in mind:

- **Never log or expose user credentials**
- **Use HTTPS for all API calls**
- **Store credentials securely (local files only)**
- **Validate all user inputs**
- **Handle sensitive data carefully**

## 📋 Pull Request Guidelines

### Before Submitting
- [ ] Code follows project style guidelines
- [ ] All tests pass
- [ ] Documentation is updated if needed
- [ ] Commit messages are clear and descriptive

### PR Description Should Include
- **What** changes were made
- **Why** the changes were necessary
- **How** to test the changes
- **Any breaking changes** or migration notes

### Example PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Tested manually
- [ ] Built executable successfully
- [ ] No regressions found

## Screenshots (if applicable)
Add screenshots for UI changes
```

## 🚀 Feature Requests

We welcome feature suggestions! When proposing new features:

1. **Check if it aligns** with project goals
2. **Consider the diabetes community** - will this help other diabetics?
3. **Think about complexity** - keep it simple and reliable
4. **Provide use cases** - when would this be useful?

### Popular Feature Ideas
- Support for other CGM systems (future)
- Customizable alert thresholds
- Historical data graphs
- Multiple widget themes
- Keyboard shortcuts

## 🐛 Bug Reports

Good bug reports help us fix issues quickly:

### Include This Information
- **Clear title** describing the issue
- **Steps to reproduce** the problem
- **Expected behavior** vs **actual behavior**
- **System information** (Windows version, Python version)
- **Error messages** or screenshots
- **Configuration details** (region, units, etc.)

### Example Bug Report
```markdown
**Title**: Widget disappears after Windows sleep/wake

**Description**: 
After my computer goes to sleep and wakes up, the glucose widget is no longer visible on the desktop.

**Steps to Reproduce**:
1. Launch cgm_simple_widget.exe
2. Position widget on desktop
3. Put computer to sleep (Windows + L, then close laptop)
4. Wake computer
5. Widget is gone

**Expected**: Widget should remain visible after wake
**Actual**: Widget disappears, need to restart application

**System**: Windows 11, Dexcom G7, Outside US region
```

## 📚 Documentation

Help improve documentation by:

- **Fixing typos** or unclear instructions
- **Adding examples** for common use cases
- **Updating screenshots** when UI changes
- **Translating** to other languages (future)
- **Writing tutorials** for specific scenarios

## 🙏 Recognition

Contributors will be recognized in:
- README.md acknowledgments
- Release notes for significant contributions
- GitHub contributors list

## ❓ Questions?

If you have questions about contributing:

1. **Check existing issues** and discussions
2. **Create a new issue** with the "question" label
3. **Be specific** about what you need help with

## 🏥 Medical Considerations

Remember that this tool is used by people managing diabetes:

- **Reliability is crucial** - bugs could affect health decisions
- **Keep it simple** - complex features can introduce errors
- **Test thoroughly** - especially error handling
- **Consider accessibility** - some users may have vision issues

Thank you for helping make glucose monitoring more accessible for the diabetes community! 🩸❤️