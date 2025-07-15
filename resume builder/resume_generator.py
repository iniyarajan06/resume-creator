import gradio as gr
from jinja2 import Environment, FileSystemLoader
import pdfkit # type: ignore
import tempfile
import traceback

# ── TEMPLATE SETUP ──────────────────────────────────────────────────────────────
env = Environment(loader=FileSystemLoader("."))
template = env.get_template("template.html")
WKHTMLTOPDF_PATH = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)

# ── RESUME GENERATION ───────────────────────────────────────────────────────────
def generate_resume(
    name, phone, email, website,
    objective,
    skills, other_skills, certifications,
    exp_table, edu_table, proj_table,
    portfolio_links
):
    try:
        skills_list = skills or []
        if other_skills:
            extras = [s.strip() for s in other_skills.split(",") if s.strip()]
            skills_list.extend(extras)

        cert_list = [c.strip() for c in certifications.split(",") if c.strip()]
        portfolio = [l.strip() for l in portfolio_links.split("\n") if l.strip()]

        experience = [
            {"role": r[0], "company": r[1], "from": r[2], "to": r[3], "description": r[4]}
            for r in exp_table if len(r) == 5 and any(r)
        ]
        education = [
            {"degree": r[0], "institution": r[1], "year": r[2]}
            for r in edu_table if len(r) == 3 and any(r)
        ]
        projects = [
            {"name": r[0], "detail": r[1]}
            for r in proj_table if len(r) == 2 and any(r)
        ]

        html = template.render(
            name=name, phone=phone, email=email, website=website,
            objective=objective,
            skills=skills_list, certifications=cert_list,
            experience=experience, education=education,
            projects=projects, portfolio_links=portfolio
        )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as out:
            pdfkit.from_string(html, out.name, configuration=config)
            return out.name

    except Exception:
        print("❌ Error in resume generation:")
        traceback.print_exc()
        raise

# ── GRADIO UI ───────────────────────────────────────────────────────────────────
with gr.Blocks(title="Resume Builder") as demo:
    gr.Markdown("## 📝 Professional Resume Builder")

    with gr.Accordion("👤 Profile", open=True):
        name = gr.Textbox(label="Full Name")
        phone = gr.Textbox(label="Phone")
        email = gr.Textbox(label="Email")
        website = gr.Textbox(label="Website")

    with gr.Accordion("🎯 Objective"):
        objective = gr.Textbox(label="Career Objective", lines=3)

    skill_choices = ["Python", "C++", "Machine Learning", "Data Science", "HTML/CSS", "JavaScript"]
    with gr.Accordion("✅ Skills & Certifications"):
        skills = gr.CheckboxGroup(label="Select Skills", choices=skill_choices)
        other_skills = gr.Textbox(label="Other Skills (comma-separated)")
        certifications = gr.Textbox(label="Certifications (comma-separated)")

    with gr.Accordion("🏢 Experience"):
        exp_table = gr.Dataframe(
            headers=["Role", "Company", "From", "To", "Description"],
            row_count=(6, "fixed"), col_count=(5, "fixed")
        )

    with gr.Accordion("🎓 Education"):
        edu_table = gr.Dataframe(
            headers=["Degree", "Institution", "Year"],
            row_count=(4, "fixed"), col_count=(3, "fixed")
        )

    with gr.Accordion("🚀 Projects"):
        proj_table = gr.Dataframe(
            headers=["Name", "Description"],
            row_count=(5, "fixed"), col_count=(2, "fixed")
        )

    with gr.Accordion("🔗 Portfolio"):
        portfolio_links = gr.Textbox(label="Portfolio Links (one per line)")

    output_pdf = gr.File(label="Download Resume PDF")
    btn = gr.Button("Generate Resume", variant="primary")

    btn.click(
        fn=generate_resume,
        inputs=[
            name, phone, email, website,
            objective,
            skills, other_skills, certifications,
            exp_table, edu_table, proj_table,
            portfolio_links
        ],
        outputs=output_pdf
    )

# ── LAUNCH ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🚀 Starting Resume Builder…")
    demo.queue()
    urls = demo.launch(
        share=True,
        inbrowser=True,
        debug=True
    )
    print("✅ Gradio app launched!")
    print(f"• Local URL:  {urls[0]}")
    print(f"• Public URL: {urls[1]}")
