
import pandas as pd
from datetime import datetime
import os
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False

class FinanceTracker:
    """
    A class to track expenses, investments, manage a budget, and persist data.
    """
    def __init__(self, expense_file='expenses.csv', investment_file='investments.csv'):
        self.expense_file = expense_file
        self.investment_file = investment_file
        self.budget = 0
        self.df = self.load_data(self.expense_file)
        self.idf = self.load_data(self.investment_file, is_investment=True)
        self.load_budget()

    def load_data(self, file_path, is_investment=False):
        """Loads data from a CSV, ensuring compatibility with new columns."""
        if os.path.exists(file_path):
            print(f"Loading data from {file_path}...")
            df = pd.read_csv(file_path)
            # Backward compatibility for expenses file
            if not is_investment and 'payment_type' not in df.columns:
                df['payment_type'] = 'Other'
            return df
        
        # Create empty DataFrame with correct columns if file doesn't exist
        columns = ["timestamp", "category", "amount"]
        if not is_investment:
            columns.append("payment_type")
        return pd.DataFrame(columns=columns)

    def save_data(self, df, file_path):
        """Saves a DataFrame to a CSV file."""
        df.to_csv(file_path, index=False)
        print(f"Data saved to {file_path}.")

    def load_budget(self):
        """Loads budget from a simple text file."""
        if os.path.exists('budget.txt'):
            with open('budget.txt', 'r') as f:
                try:
                    self.budget = float(f.read())
                    print(f"Budget of {self.budget} loaded.")
                except ValueError:
                    self.budget = 0

    def save_budget(self):
        """Saves budget to a text file for persistence."""
        with open('budget.txt', 'w') as f:
            f.write(str(self.budget))

    def set_budget(self, amount):
        """Sets the monthly budget and saves it."""
        self.budget = amount
        self.save_budget()
        print(f"🎯 Budget set to: {self.budget}")

    def add_expense(self, category, amount, payment_type):
        """Adds a new expense with a timestamp and payment type."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = pd.DataFrame([{"timestamp": timestamp, "category": category, "amount": amount, "payment_type": payment_type}])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self.save_data(self.df, self.expense_file)
        print(f"✅ Added Expense: {amount} in {category} (Type: {payment_type})")
        
    def add_investment(self, category, amount):
        """Adds a new investment with a timestamp."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = pd.DataFrame([{"timestamp": timestamp, "category": category, "amount": amount}])
        self.idf = pd.concat([self.idf, new_row], ignore_index=True)
        self.save_data(self.idf, self.investment_file)
        print(f"📈 Added Investment: {amount} in {category}")

    def list_expenses(self):
        """Displays a numbered list of all expenses."""
        if self.df.empty:
            print("\n📊 No expenses yet.")
            return False
            
        print("\n========== 🧾 All Expenses ==========")
        print(self.df.to_string(index=True))
        print("======================================")
        return True

    def delete_expense(self, index):
        """Deletes an expense by its index."""
        try:
            self.df = self.df.drop(self.df.index[index]).reset_index(drop=True)
            self.save_data(self.df, self.expense_file)
            print(f"🗑️ Expense at index {index} deleted.")
        except IndexError:
            print("❌ Invalid index. Please choose a number from the list.")
            
    def clear_all_expenses(self):
        """Deletes all expense data after confirmation."""
        confirm = input("Are you sure you want to delete ALL expenses? This cannot be undone. Type 'yes' to confirm: ").lower()
        if confirm == 'yes':
            self.df = pd.DataFrame(columns=["timestamp", "category", "amount", "payment_type"])
            if os.path.exists(self.expense_file):
                os.remove(self.expense_file)
            print("💥 All expenses have been cleared.")
        else:
            print("Operation cancelled.")

    def get_monthly_summary_data(self):
        """Helper function to get all summary data for the current month."""
        if self.df.empty:
            return None

        self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        now = datetime.now()
        monthly_df = self.df[(self.df['timestamp'].dt.month == now.month) & (self.df['timestamp'].dt.year == now.year)]

        if monthly_df.empty:
            return None
        
        total_spent = monthly_df['amount'].sum()
        category_summary = monthly_df.groupby("category")['amount'].sum().reset_index()
        category_summary['percentage'] = (category_summary['amount'] / total_spent * 100).round(2)
        category_summary = category_summary.sort_values(by='amount', ascending=False)
        
        type_summary = monthly_df.groupby('payment_type')['amount'].sum()
        upi_total = type_summary.get('UPI', 0)
        other_total = type_summary.get('Other', 0)
        
        savings = self.budget - total_spent if self.budget > 0 else 0

        return {
            "month_name": now.strftime('%B %Y'),
            "category_summary": category_summary,
            "total_spent": total_spent,
            "upi_total": upi_total,
            "other_total": other_total,
            "budget": self.budget,
            "savings": savings
        }

    def summary(self):
        """Provides a detailed summary of expenses for the CURRENT MONTH."""
        data = self.get_monthly_summary_data()

        if not data:
            print(f"\n📊 No expenses recorded for the current month ({datetime.now().strftime('%B %Y')}).")
            return
            
        print(f"\n========== 📊 Expense Summary for {data['month_name']} ==========")
        # ... existing summary code ...
        print("\n--- Spending by Category ---")
        print(data['category_summary'].to_string(index=False))
        
        print("\n--- Spending by Type ---")
        print(f"UPI Payments:   ₹{data['upi_total']:.2f}")
        print(f"Other Expenses: ₹{data['other_total']:.2f}")

        print("\n--- Overall Summary ---")
        print(f"💵 Total Spent:  ₹{data['total_spent']:.2f}")
        print(f"🎯 Budget:       ₹{data['budget']:.2f}" if data['budget'] > 0 else "🎯 Budget: Not set")
        
        if data['budget'] > 0:
            if data['savings'] >= 0:
                print(f"✅ Money Saved:  ₹{data['savings']:.2f}")
            else:
                print(f"⚠️ Money Overspent: ₹{-data['savings']:.2f}")
        print("====================================================")

    def investment_summary(self):
        """Provides a summary of all investments."""
        if self.idf.empty:
            print("\n📈 No investments recorded yet.")
            return

        total_invested = self.idf['amount'].sum()
        summary = self.idf.groupby('category')['amount'].sum().sort_values(ascending=False)
        
        print("\n========== 📈 Investment Summary ==========")
        print(summary.to_string())
        print("------------------------------------------")
        print(f"💰 Total Invested: ₹{total_invested:.2f}")
        print("==========================================")


    def generate_pdf_report(self):
        """Generates a PDF report of the current month's expense summary."""
        # ... existing PDF generation code ...
        if not FPDF_AVAILABLE:
            print("\n❌ PDF generation failed. Please install the FPDF library:")
            print("👉 pip install fpdf2")
            return

        data = self.get_monthly_summary_data()
        if not data:
            print(f"\n📊 No expenses to report for {datetime.now().strftime('%B %Y')}.")
            return
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 18)
        
        pdf.cell(0, 10, f"Expense Report - {data['month_name']}", 0, 1, 'C')
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Overall Summary", 0, 1)
        pdf.set_font("Arial", '', 12)
        
        summary_items = [
            ["Total Spent:", f"Rs. {data['total_spent']:.2f}"],
            ["Monthly Budget:", f"Rs. {data['budget']:.2f}" if data['budget'] > 0 else "Not set"],
            ["Total Savings:" if data['savings'] >= 0 else "Amount Overspent:", f"Rs. {abs(data['savings']):.2f}"]
        ]
        
        for item in summary_items:
            pdf.cell(50, 8, item[0], 0, 0)
            pdf.cell(0, 8, item[1], 0, 1)
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, "Spending by Category", 0, 1)
        pdf.set_font("Arial", 'B', 10)
        
        pdf.cell(80, 8, "Category", 1, 0, 'C')
        pdf.cell(50, 8, "Amount (Rs.)", 1, 0, 'C')
        pdf.cell(40, 8, "Percentage (%)", 1, 1, 'C')

        pdf.set_font("Arial", '', 10)
        for _, row in data['category_summary'].iterrows():
            pdf.cell(80, 8, str(row['category']), 1, 0)
            pdf.cell(50, 8, f"{row['amount']:.2f}", 1, 0, 'R')
            pdf.cell(40, 8, f"{row['percentage']:.2f}", 1, 1, 'R')

        file_name = f"Expense_Report_{datetime.now().strftime('%B_%Y')}.pdf"
        pdf.output(file_name)
        print(f"\n📄 Successfully generated PDF report: {file_name}")


# ------------------- Main Program -------------------
def main():
    """The main function to run the Finance Bot CLI."""
    bot = FinanceTracker()

    while True:
        print("\n========== Smart Finance Bot v4.0 ==========")
        print("1️⃣  Add Expense")
        print("2️⃣  Add Investment")
        print("3️⃣  View Monthly Expense Summary")
        print("4️⃣  View Investment Summary")
        print("5️⃣  Set/Change Budget")
        print("6️⃣  List & Delete Expense")
        print("7️⃣  Generate PDF Report")
        print("8️⃣  Clear All Expenses")
        print("9️⃣  Exit")
        print("==========================================")

        choice = input("👉 Enter choice: ")

        if choice == "1":
            category = input("Enter expense category (e.g., Food, Rent): ").strip().title()
            try:
                amount = float(input("Enter amount: "))
                pt_choice = ""
                while pt_choice not in ['1', '2']:
                    pt_choice = input("Enter payment type (1 for UPI, 2 for Other): ").strip()
                payment_type = 'UPI' if pt_choice == '1' else 'Other'
                bot.add_expense(category, amount, payment_type)
            except ValueError:
                print("❌ Invalid amount. Please enter a number.")
        
        elif choice == "2":
            category = input("Enter investment category (e.g., Stocks, Mutual Fund): ").strip().title()
            try:
                amount = float(input("Enter amount: "))
                bot.add_investment(category, amount)
            except ValueError:
                print("❌ Invalid amount. Please enter a number.")

        elif choice == "3":
            bot.summary()

        elif choice == "4":
            bot.investment_summary()

        elif choice == "5":
            try:
                budget = float(input("Enter new budget: "))
                bot.set_budget(budget)
            except ValueError:
                print("❌ Invalid amount. Please enter a number.")

        elif choice == "6":
            if bot.list_expenses():
                try:
                    idx_to_delete_str = input("Enter the number of the expense to delete (or press Enter to skip): ")
                    if idx_to_delete_str:
                        bot.delete_expense(int(idx_to_delete_str))
                except ValueError:
                    print("Skipping deletion or invalid number.")
        
        elif choice == "7":
            bot.generate_pdf_report()
            
        elif choice == "8":
            bot.clear_all_expenses()

        elif choice == "9":
            print("👋 Goodbye! Stay financially smart!")
            break

        else:
            print("❌ Invalid choice, please try again.")

if __name__ == "__main__":
    main()

