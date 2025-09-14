import pandas as pd

class FinanceBot:
    def __init__(self, budget=0):
        self.expenses = []
        self.budget = budget

    def set_budget(self, amount):
        self.budget = amount
        print(f"🎯 Budget set to: {self.budget}")

    def add_expense(self, category, amount):
        self.expenses.append({"category": category, "amount": amount})
        print(f"✅ Added: {amount} in {category}")

    def summary(self):
        if not self.expenses:
            print("\n📊 No expenses yet.")
            return

        df = pd.DataFrame(self.expenses)
        summary = df.groupby("category").sum()

        print("\n========== 📊 Expense Summary ==========")
        print(summary)
        print("========================================")

        total = df["amount"].sum()
        print(f"\n💵 Total Spent: {total}")
        print(f"🎯 Budget: {self.budget if self.budget else 'Not set'}")

        if self.budget:
            if total > self.budget:
                print("⚠️ ALERT: You have crossed your budget!")
            elif total > (0.8 * self.budget):
                print("⚠️ Warning: You are close to your budget limit!")
            else:
                print(f"✅ Safe: You are within budget. Remaining: {self.budget - total}")

# ------------------- Main Program -------------------
if __name__ == "__main__":
    bot = FinanceBot()

    while True:
        print("\n========== Smart Finance Bot ==========")
        print("1️⃣  Add Expense")
        print("2️⃣  View Summary")
        print("3️⃣  Set/Change Budget")
        print("4️⃣  Exit")
        print("=======================================")

        choice = input("👉 Enter choice: ")

        if choice == "1":
            category = input("Enter category (Food, Rent, etc.): ")
            try:
                amount = float(input("Enter amount: "))
                bot.add_expense(category, amount)
            except ValueError:
                print("❌ Please enter a valid number.")

        elif choice == "2":
            bot.summary()

        elif choice == "3":
            try:
                budget = float(input("Enter new budget: "))
                bot.set_budget(budget)
            except ValueError:
                print("❌ Please enter a valid number.")

        elif choice == "4":
            print("👋 Goodbye! Stay financially smart!")
            break

        else:
            print("❌ Invalid choice, try again.")
