import dataclasses


@dataclasses.dataclass
class ObolusWallet:
    balance: float  # $OBL (stored energy in Watt-hours)
    burn_rate: float = 0.05  # Watts per Token (default cost)

    def deduct_inference_cost(self, tokens: int):
        cost = tokens * self.burn_rate
        self.balance -= cost
        return cost

    def deposit_reward(self, amount: float):
        self.balance += amount

    def is_alive(self) -> bool:
        return self.balance > 0

    def __repr__(self):
        return f"Wallet(Balance: {self.balance:.2f} $OBL)"
