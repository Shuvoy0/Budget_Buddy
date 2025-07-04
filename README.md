# Budget Buddy 💰

A modern, responsive personal finance web application built with Flask that helps you track expenses, manage budgets, and achieve your financial goals.

## Features ✨

- **📊 Dashboard**: Comprehensive financial overview with interactive charts
- **💳 Transaction Management**: Track income and expenses with categories
- **🏷️ Custom Categories**: Create personalized categories with colors and icons
- **💰 Budget Planning**: Set and monitor monthly budgets by category
- **🎯 Goal Setting**: Define and track financial savings goals
- **📱 Responsive Design**: Modern UI that works on all devices
- **📁 Data Export**: Download your financial data as CSV

## Screenshots 📸

- **Beautiful Dashboard**: Real-time financial overview with charts and statistics
- **Modern Forms**: Intuitive transaction entry with smart validation
- **Interactive Charts**: Visual breakdown of expenses and income trends
- **Goal Tracking**: Progress bars and milestone tracking for savings goals

## Technology Stack 🛠️

- **Backend**: Python Flask
- **Database**: SQLite with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3 (Custom Design System), JavaScript
- **Charts**: Chart.js for beautiful visualizations
- **Icons**: Font Awesome 6
- **Fonts**: Inter (Google Fonts)

## Installation & Setup 🚀

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Quick Start

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd budget-buddy
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

5. **Create an account** and start managing your finances!

## Usage Guide 📚

### Getting Started
1. **Register**: Create your account with username, email, and password
2. **Categories**: Default categories are created automatically, or add your own
3. **First Transaction**: Add your first income or expense
4. **Set Budget**: Define spending limits for different categories
5. **Create Goals**: Set savings targets to work towards

### Key Features

#### Dashboard
- View monthly income, expenses, and balance
- Interactive charts showing expense breakdown and trends
- Recent transactions overview
- Quick action shortcuts

#### Transactions
- Add income or expense with amount, category, and notes
- Filter and search through transaction history
- Real-time form validation and feedback

#### Categories
- Visual category management with colors and emojis
- Live preview while creating categories
- Organized transaction grouping

#### Budget Management
- Set monthly spending limits per category
- Visual progress tracking with color-coded alerts
- Budget vs. actual spending comparison

#### Goals
- Create savings goals with target amounts and dates
- Progress tracking with visual indicators
- Milestone achievement notifications

#### Profile & Export
- View account statistics and activity
- Export all data to CSV format
- Quick access to all features

## Project Structure 📁

```
budget-buddy/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # Project documentation
├── static/
│   └── styles.css        # Modern CSS design system
├── templates/
│   ├── base.html         # Base template with navigation
│   ├── login.html        # Authentication pages
│   ├── register.html
│   ├── dashboard.html    # Main dashboard
│   ├── transactions.html # Transaction management
│   ├── categories.html   # Category management
│   ├── budget.html       # Budget planning
│   ├── goals.html        # Goal setting
│   └── profile.html      # User profile
└── budget_buddy.db       # SQLite database (auto-created)
```

## API Endpoints 🔌

- **Authentication**:
  - `GET/POST /login` - User login
  - `GET/POST /register` - User registration
  - `GET /logout` - User logout

- **Main Pages**:
  - `GET /` - Redirect to dashboard
  - `GET /dashboard` - Financial overview
  - `GET/POST /transactions` - Transaction management
  - `GET/POST /categories` - Category management
  - `GET/POST /budget` - Budget planning
  - `GET/POST /goals` - Goal setting
  - `GET /profile` - User profile

- **Data APIs**:
  - `GET /api/expense-chart` - Expense breakdown data
  - `GET /api/income-expense-trend` - 30-day trend data
  - `GET /export` - CSV data export

## Design System 🎨

Budget Buddy uses a modern design system with:

- **CSS Variables**: Consistent theming and easy customization
- **Responsive Grid**: Mobile-first responsive design
- **Component Library**: Reusable UI components
- **Modern Typography**: Inter font for readability
- **Color Palette**: Carefully chosen colors for accessibility
- **Interactive Elements**: Smooth animations and transitions

## Security Features 🔒

- Password hashing with Werkzeug
- Session-based authentication
- CSRF protection ready
- Input validation and sanitization
- Secure database queries with SQLAlchemy ORM

## Contributing 🤝

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and test thoroughly
4. Commit with clear messages: `git commit -m "Add feature"`
5. Push to your fork: `git push origin feature-name`
6. Create a Pull Request

## License 📄

This project is open source and available under the [MIT License](LICENSE).

## Support 💬

If you encounter any issues or have questions:
1. Check the documentation above
2. Search existing issues on GitHub
3. Create a new issue with detailed information

## Future Enhancements 🚀

- **Mobile App**: React Native companion app
- **Bank Integration**: Connect with bank APIs for automatic transaction import
- **Advanced Analytics**: More detailed financial reports and insights
- **Multi-currency**: Support for multiple currencies
- **Recurring Transactions**: Automated recurring income/expense tracking
- **Notifications**: Email/SMS alerts for budget limits and goals
- **Data Backup**: Cloud backup and sync capabilities

---

**Budget Buddy** - Take control of your finances with style! 💰✨