import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("symbol", sa.String(12), nullable=False),
        sa.Column("side", sa.String(4), nullable=False),
        sa.Column("quantity", sa.Numeric(20, 6), nullable=False),
        sa.Column("price", sa.Numeric(20, 4), nullable=False),
        sa.Column("fee", sa.Numeric(20, 4), nullable=False),
        sa.Column("executed_at", sa.Date(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("side IN ('buy', 'sell')", name="ck_transactions_side"),
        sa.CheckConstraint("quantity > 0", name="ck_transactions_quantity_positive"),
        sa.CheckConstraint("price > 0", name="ck_transactions_price_positive"),
        sa.CheckConstraint("fee >= 0", name="ck_transactions_fee_non_negative"),
    )
    op.create_index("ix_transactions_symbol", "transactions", ["symbol"])
    op.create_index("ix_transactions_executed_at", "transactions", ["executed_at"])
    op.create_table(
        "prices",
        sa.Column("symbol", sa.String(12), primary_key=True),
        sa.Column("price", sa.Numeric(20, 4), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("price > 0", name="ck_prices_price_positive"),
    )


def downgrade() -> None:
    op.drop_table("prices")
    op.drop_index("ix_transactions_executed_at", table_name="transactions")
    op.drop_index("ix_transactions_symbol", table_name="transactions")
    op.drop_table("transactions")
