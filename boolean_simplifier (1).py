import streamlit as st
import pandas as pd
import itertools
import ast

from sympy import Symbol, true, false
from sympy.logic.boolalg import And, Or, Not, Xor, simplify_logic
from sympy.core import count_ops


st.set_page_config(
    page_title="Boolean Expression Simplifier",
    layout="wide"
)


st.markdown("""
<style>
.stApp {
    background-color: #f4f6fa;
}
h1, h2, h3 {
    color: #19365c;
}
.result {
    background-color: #e8f5e9;
    padding: 20px;
    border-radius: 8px;
    color: #174b2a;
    font-size: 22px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)


def parse_expression(expression):

    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError:
        raise ValueError("Invalid expression syntax.")

    variables = set()

    def convert(node):

        if isinstance(node, ast.Name):
            variables.add(node.id)
            return Symbol(node.id)

        if isinstance(node, ast.Constant):
            if node.value in (0, 1, True, False):
                return true if bool(node.value) else false
            raise ValueError("Only 0 and 1 are allowed.")

        if isinstance(node, ast.BinOp):

            left = convert(node.left)
            right = convert(node.right)

            if isinstance(node.op, ast.BitAnd):
                return And(left, right)

            if isinstance(node.op, ast.BitOr):
                return Or(left, right)

            if isinstance(node.op, ast.BitXor):
                return Xor(left, right)

            raise ValueError("Unsupported operator.")

        if isinstance(node, ast.UnaryOp):

            operand = convert(node.operand)

            if isinstance(node.op, (ast.Invert, ast.Not)):
                return Not(operand)

            raise ValueError("Unsupported operator.")

        raise ValueError("Invalid expression.")

    result = convert(tree.body)

    if len(variables) > 8:
        raise ValueError("Maximum 8 variables are allowed.")

    return result, sorted(variables)


def simplify_expression(expression):

    dnf = simplify_logic(
        expression,
        form="dnf",
        force=True
    )

    cnf = simplify_logic(
        expression,
        form="cnf",
        force=True
    )

    return dnf, cnf


def generate_truth_table(expression, variables):

    rows = []

    for values in itertools.product(
        [0, 1],
        repeat=len(variables)
    ):

        substitution = {
            Symbol(variable): bool(value)
            for variable, value in zip(variables, values)
        }

        output = int(bool(expression.subs(substitution)))

        row = dict(zip(variables, values))
        row["Output"] = output

        rows.append(row)

    return pd.DataFrame(rows)


st.sidebar.title("Navigation")

page = st.sidebar.radio(
    "Select Section",
    [
        "Dashboard",
        "Expression Simplifier",
        "Truth Table Generator",
        "Boolean Algebra Laws",
        "About Project"
    ]
)


st.title("Boolean Expression Simplification System")

st.caption(
    "Python Based Boolean Algebra Application"
)

st.divider()


if page == "Dashboard":

    st.header("Dashboard")

    st.write(
        "A system for simplifying complex Boolean expressions "
        "using Boolean algebra and symbolic logic."
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Logical Operators", "3")
    col2.metric("Maximum Variables", "8")
    col3.metric("Output Forms", "2")

    st.subheader("Features")

    col1, col2 = st.columns(2)

    with col1:
        st.info("Boolean Expression Simplification")
        st.info("Truth Table Generation")
        st.info("DNF Generation")

    with col2:
        st.info("CNF Generation")
        st.info("Boolean Algebra Laws")
        st.info("CSV Download")


elif page == "Expression Simplifier":

    st.header("Expression Simplifier")

    st.write("Enter a Boolean expression.")

    st.caption("AND: &, OR: |, NOT: ~, XOR: ^")

    user_expression = st.text_input(
        "Boolean Expression",
        value="(A & B) | (A & ~B)"
    )

    if st.button("Simplify Expression", type="primary"):

        try:

            original, variables = parse_expression(
                user_expression
            )

            dnf, cnf = simplify_expression(original)

            st.success("Expression simplified successfully.")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Original Expression")
                st.code(user_expression)

            with col2:
                st.subheader("Simplified DNF")
                st.code(str(dnf))

            st.subheader("Simplified CNF")
            st.code(str(cnf))

            st.divider()

            st.subheader("Expression Analysis")

            col1, col2, col3 = st.columns(3)

            col1.metric("Variables", len(variables))

            col2.metric(
                "Original Operations",
                int(count_ops(original))
            )

            col3.metric(
                "Simplified Operations",
                int(count_ops(dnf))
            )

            if count_ops(dnf) < count_ops(original):
                st.success("Expression complexity has been reduced.")
            else:
                st.info("Expression is already simplified or has equal complexity.")

            st.session_state["original"] = original
            st.session_state["dnf"] = dnf
            st.session_state["cnf"] = cnf
            st.session_state["variables"] = variables

        except Exception as error:
            st.error(str(error))


elif page == "Truth Table Generator":

    st.header("Truth Table Generator")

    expression_input = st.text_input(
        "Enter Boolean Expression",
        value="A & B | ~A"
    )

    if st.button("Generate Truth Table", type="primary"):

        try:

            expression, variables = parse_expression(
                expression_input
            )

            table = generate_truth_table(
                expression,
                variables
            )

            st.success("Truth table generated successfully.")

            st.dataframe(
                table,
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                "Download Truth Table",
                table.to_csv(index=False),
                file_name="truth_table.csv",
                mime="text/csv"
            )

        except Exception as error:
            st.error(str(error))


elif page == "Boolean Algebra Laws":

    st.header("Boolean Algebra Laws")

    laws = {
        "Identity Law":
            "A + 0 = A, A . 1 = A",

        "Null Law":
            "A + 1 = 1, A . 0 = 0",

        "Idempotent Law":
            "A + A = A, A . A = A",

        "Complement Law":
            "A + A' = 1, A . A' = 0",

        "Double Negation Law":
            "(A')' = A",

        "Commutative Law":
            "A + B = B + A",

        "Associative Law":
            "(A + B) + C = A + (B + C)",

        "Distributive Law":
            "A(B + C) = AB + AC",

        "Absorption Law":
            "A + AB = A",

        "De Morgan's Law":
            "(A.B)' = A' + B'"
    }

    for law, formula in laws.items():

        with st.expander(law):
            st.write(formula)


elif page == "About Project":

    st.header("About Project")

    st.subheader("Project Description")

    st.write(
        "Boolean Expression Simplification System is a "
        "Python-based application developed to simplify "
        "complex Boolean expressions into equivalent "
        "simplified forms."
    )

    st.subheader("Objectives")

    st.write("""
    - Simplify complex Boolean expressions.
    - Generate truth tables automatically.
    - Display DNF and CNF forms.
    - Reduce manual calculation efforts.
    - Provide an interactive interface.
    """)

    st.subheader("Technologies Used")

    st.write("""
    - Python
    - Streamlit
    - SymPy
    - Pandas
    """)

    st.subheader("Applications")

    st.write("""
    - Digital Electronics
    - Digital Logic Design
    - Computer Engineering
    - Logic Circuit Design
    """)

    st.success("Thank you for using the application.")