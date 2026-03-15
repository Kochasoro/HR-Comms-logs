"""add default users

Revision ID: 5d4983c032b0
Revises: 094c5a6ae500
Create Date: 2026-03-11 16:47:14.630504
"""

from alembic import op
import sqlalchemy as sa
from werkzeug.security import generate_password_hash


# revision identifiers
revision = '5d4983c032b0'
down_revision = '094c5a6ae500'
branch_labels = None
depends_on = None


def upgrade():

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password_hash', sa.String(length=255), nullable=False))
        batch_op.alter_column(
            'username',
            existing_type=sa.VARCHAR(length=50),
            nullable=False
        )
        batch_op.drop_column('password')

    # ---- CREATE DEFAULT USERS ----

    conn = op.get_bind()

    conn.execute(
        sa.text("""
        INSERT INTO users (username, password_hash, role)
        VALUES
        (:Superadmin, :pass1, 'admin'),
        (:Admin, :pass2, 'admin'),
        (:secretary, :pass3, 'secretary')
        """),
        {
            "Superadmin": "Superadmin",
            "pass1": generate_password_hash("OJTAccess"),

            "Admin": "Admin",
            "pass2": generate_password_hash("Password"),

            "secretary": "secretary",
            "pass3": generate_password_hash("secret123"),
        }
    )


def downgrade():

    conn = op.get_bind()

    conn.execute(sa.text("""
        DELETE FROM users
        WHERE username IN ('Superadmin','Admin','secretary')
    """))

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('password', sa.VARCHAR(length=255), nullable=True))
        batch_op.alter_column(
            'username',
            existing_type=sa.VARCHAR(length=50),
            nullable=True
        )
        batch_op.drop_column('password_hash')