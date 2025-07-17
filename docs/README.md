# Dexcom Windows Widget 🩸

A simple, lightweight desktop widget for diabetics to monitor their Dexcom G7 glucose readings directly on their Windows PC.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Dexcom](https://img.shields.io/badge/Dexcom-G7-green.svg)

## 🎯 Purpose

This tool was created by a diabetic, for diabetics. It provides a simple way to keep your Dexcom G7 glucose readings visible on your desktop without having to constantly check your phone or Dexcom receiver.

Here I have it on the top bar of VS Code.

<img width="442" height="196" alt="image" src="https://github.com/user-attachments/assets/128d45b3-5a56-4905-a7a3-b777b16345c3" />

## ⚠️ Important Medical Disclaimer

**This software is for informational purposes only and is not a medical device.** 

- Always use your official Dexcom app/receiver for medical decisions
- This tool should supplement, not replace, proper diabetes management
- Consult your healthcare provider for all medical decisions
- The developers are not medical professionals
- This is an unofficial tool not affiliated with Dexcom, Inc.

## ✨ Features

- **Always visible** - Small desktop widget that stays on top
- **Real-time updates** - Refreshes every minute using Dexcom Share API
- **Color-coded readings** - Green (normal), Orange (high), Red (low)
- **Trend arrows** - Shows glucose direction and rate of change
- **Draggable** - Position anywhere on your screen
- **Multiple units** - Supports both mg/dL and mmol/L
- **Easy setup** - Simple credential entry on first run
- **Lightweight** - Minimal system resources
- **Secure** - Credentials stored locally only

## 📋 Requirements

### Dexcom Setup
1. **Dexcom G7** with the official Dexcom app installed
2. **Dexcom Share enabled** - Follow [Dexcom's instructions](https://provider.dexcom.com/education-research/cgm-education-use/videos/setting-dexcom-share-and-follow)
3. **Email-based account** - Phone number logins may not work

**Note**: No followers are required when using your own Dexcom account that's signed into the G7 app.

### System Requirements
- **Windows 10/11**
- **Internet connection**
- **Python 3.8+** (for building from source)

## 🚀 Quick Start

### Option 1: Use Pre-built Executable

1. Download the latest `cgm_simple_widget.exe` from the releases
2. Double-click to run
3. Enter your Dexcom credentials when prompted
4. Select your region (US, Outside US, or Japan)
5. Widget appears on your desktop!

### Option 2: Build from Source

1. **Clone the repository**:
   ```bash
   git clone https://github.com/KristianSv/dexcom-win-widget.git
   cd dexcom-win-widget
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run directly**:
   ```bash
   python cgm_simple_widget.py
   ```

4. **Or build executable**:
   ```bash
   python build_executable.py
   ```

## 🔧 Building Your Own Executable

See [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) for detailed build instructions.

Quick build:
```bash
python -m PyInstaller --onefile --windowed cgm_simple_widget.py
```

## 🎮 Usage

1. **First Run**: Enter your Dexcom Share credentials
2. **Widget Controls**:
   - **Drag** to move the widget
   - **Left-click** to show detailed glucose information
   - **Right-click** for menu (Details, Refresh, Exit)
3. **Configuration**: Settings saved in `cgm_config.json`

## 🌍 Supported Regions

- **United States** (us)
- **Outside United States** (ous) 
- **Japan** (jp)

## 🔒 Security & Privacy

- **Local storage only** - Credentials never leave your computer
- **HTTPS connections** - All API calls use secure connections
- **No telemetry** - No usage data collected
- **Open source** - Full code transparency

## 🐛 Troubleshooting

### Common Issues

**"Invalid Password" Error**:
- Verify credentials on [Dexcom website](https://uam1.dexcom.com) (US) or [uam2.dexcom.com](https://uam2.dexcom.com) (Outside US)
- Ensure Dexcom Share is enabled in your Dexcom app
- Try using your account ID instead of username

**No Glucose Data**:
- Check that your Dexcom sensor is active and transmitting
- Verify Share service is enabled in your Dexcom app
- Ensure you have recent readings (within 24 hours)

**Widget Not Appearing**:
- Check for error messages in the console
- Try running as administrator
- Verify all dependencies are installed

## 🤝 Contributing

Contributions are welcome! This project aims to help the diabetes community.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚖️ Legal

This is an unofficial tool that uses the Dexcom Share API. It is not affiliated with, endorsed by, or supported by Dexcom, Inc. Dexcom is a trademark of Dexcom, Inc.

## 🙏 Acknowledgments

- Built with [pydexcom](https://github.com/gagebenne/pydexcom) library
- Created for the diabetes community
- Inspired by the need for accessible glucose monitoring

## 🤖 Development Credits

This project was developed through an AI-human collaboration:

- **AI Development**: The Python code was written almost exclusively by **Roo Code** using the **Claude Sonnet 4** model
- **Project Lead & Planning**: **Kristian** (specializing in .NET and TypeScript) provided the vision, requirements, testing, and close collaboration throughout the development process
- **Collaboration Model**: This represents a successful example of AI-assisted development where domain expertise and AI capabilities combined to create a useful tool for the diabetes community

The project demonstrates how AI can help bring ideas to life even when the project lead's primary expertise lies in different technologies (.NET/TypeScript vs Python).

---

**Remember**: This tool is meant to supplement, not replace, proper diabetes management. Always consult with your healthcare provider for medical decisions.
