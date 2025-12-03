# Fitts' Law and Affordances in HCI

## Fitts' Law

- **Fitts' Law** predicts the time it takes to **point** to a target (e.g., with a mouse).
- Classic formula (one common form):

  - MT = a + b * log2( (D / W) + 1 )

  where:
  - MT = movement time
  - D = distance to the target
  - W = width of the target
  - a, b = constants determined experimentally

- Interpretation:
  - The movement time increases as:
    - **Distance (D)** increases.
    - **Width (W)** decreases.
  - So targets that are **far away** or **very small** are slower and harder to click.

### Design implications

- Make frequently used targets **larger** and **closer**.
- Put important buttons near where the cursor or finger already is.
- Edges and corners of the screen can be effective target areas.

---

## Affordances

- An **affordance** is a property of an object that **suggests a possible action**.
- In interaction design, an affordance is about **perceived** action possibilities.

### Examples

- A **button** that looks raised and clickable suggests “press me”.
- A **scroll bar** suggests that the content can be scrolled.
- A **text field** with a visible cursor suggests that you can type.

### Good vs poor affordances

- Good affordances:
  - Make the intended action obvious.
  - Reduce errors and confusion.
- Poor affordances:
  - Icons or controls that look clickable but are not.
  - Text that looks like a link but does nothing.

### Relationship to signifiers

- **Signifiers** are signals that draw attention to the affordance (e.g., labels, icons).
- A good design often combines clear **affordances** with strong **signifiers**.
