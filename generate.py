#!/usr/bin/env python3

import html
import os
import sys
import yaml

from pathlib import Path
from typing import Any, Dict, List


def escape_html(text: Any) -> str:
    if text is None:
        return ""

    return html.escape(str(text), quote=True).replace("'", "&#039;")


def format_multiline(text: Any) -> str:
    if not text:
        return ""
    lines = [ln.strip() for ln in str(text).split("\n")]
    lines = [ln for ln in lines if ln]
    return "\n".join(lines)


def generate_page(resume: Dict[str, Any]) -> str:
    personal = resume.get("personal", {})
    summary = resume.get("summary", "")
    experience = resume.get("experience", []) or []
    projects = resume.get("projects", []) or []
    volunteering = resume.get("volunteering", []) or []
    skills = resume.get("skills", {}) or {}
    education = resume.get("education", []) or []
    languages = resume.get("languages", []) or []

    name = personal.get("name", "")
    name_parts = str(name).split(" ") if name else []
    first_name = name_parts[0] if len(name_parts) > 0 else ""
    last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

    links: List[Dict[str, str]] = []
    personal_links = (personal.get("links") or {})

    gh = personal_links.get("github")
    if isinstance(gh, dict) and gh.get("url"):
        links.append({"icon": "Github", "label": gh.get("username", ""), "href": gh.get("url", "")})

    li = personal_links.get("linkedin")
    if isinstance(li, dict) and li.get("url"):
        links.append({"icon": "Linkedin", "label": "LinkedIn", "href": li.get("url", "")})

    em = personal_links.get("email")
    if isinstance(em, dict) and em.get("address"):
        links.append({"icon": "Mail", "label": "Email", "href": f"mailto:{em.get('address')}"})

    tg = personal_links.get("telegram")
    if isinstance(tg, dict) and tg.get("url"):
        links.append({"icon": "MessageCircle", "label": tg.get("username", ""), "href": tg.get("url", "")})

    icons_import = ", ".join([l["icon"] for l in links]) if links else ""

    def render_links() -> str:
        out: List[str] = []
        for link in links:
            href = link.get("href", "")
            attrs = ""
            if href.startswith("http"):
                attrs = 'target="_blank"\n                  rel="noopener noreferrer"'
            out.append(
                f'''                <a
                  href="{escape_html(href)}"
                  {attrs}
                  className="flex items-center gap-2 hover:text-primary transition-colors px-4 py-2 rounded-lg hover:bg-card"
                >
                  <{link["icon"]} className="w-5 h-5" />
                  {escape_html(link.get("label",""))}
                </a>'''
            )
        return "\n".join(out)

    def render_experience() -> str:
        blocks: List[str] = []
        for exp in experience:
            responsibilities = exp.get("responsibilities", []) or []
            resp_lines = "\n".join(
                [
                    f'''                  <li className="flex items-start gap-3">
                    <span className="text-primary mt-2">▸</span>
                    <span>{escape_html(resp)}</span>
                  </li>'''
                    for resp in responsibilities
                ]
            )
            blocks.append(
                f'''              <div className="relative pl-8 border-l-4 border-primary">
                <div className="absolute -left-2 top-0 w-4 h-4 bg-primary rounded-full"></div>
                <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-3">
                  <h3 className="text-2xl font-semibold text-foreground">
                    {escape_html(exp.get("title",""))}
                  </h3>
                  <span className="text-primary font-medium text-lg">{escape_html(exp.get("period",""))}</span>
                </div>
                <p className="text-primary mb-5 font-medium text-lg">{escape_html(exp.get("company",""))}</p>
                <ul className="space-y-2.5 text-foreground list-none">
{resp_lines}
                </ul>
              </div>'''
            )
        return "\n\n".join(blocks)

    def render_projects() -> str:
        blocks: List[str] = []
        for proj in projects:
            span_class = "md:col-span-2" if proj.get("span") == 2 else ""
            desc = proj.get("description")
            desc_block = ""
            if isinstance(desc, str) and desc.strip():
                desc_block = f'''                <p className="text-foreground mb-3 text-sm">{escape_html(desc.strip())}</p>'''
            points = proj.get("points", []) or []
            points_block = ""
            if points:
                points_lines = "\n".join(
                    [
                        f'''                  <li className="flex items-start gap-2">
                    <span className="text-primary mt-1.5 text-xs">▸</span>
                    <span className="text-sm">{escape_html(point)}</span>
                  </li>'''
                        for point in points
                    ]
                )
                points_block = f'''                <ul className="space-y-2 text-foreground list-none">
{points_lines}
                </ul>'''
            blocks.append(
                f'''              <div className="bg-card p-6 rounded-xl border-2 border-border hover:border-primary transition-colors shadow-lg {span_class}">
                <div className="flex flex-col mb-4">
                  <h3 className="text-xl font-semibold text-foreground mb-2">
                    {escape_html(proj.get("title",""))}
                  </h3>
                  <span className="text-primary font-medium">{escape_html(proj.get("period",""))}</span>
                </div>
{desc_block}
{points_block}
              </div>'''
            )
        return "\n\n".join(blocks)

    def render_volunteering() -> str:
        if not volunteering:
            return ""
        blocks: List[str] = []
        for vol in volunteering:
            org = vol.get("organization")
            org_block = ""
            if org:
                org_block = f'''                <p className="text-primary mb-3 font-medium text-lg">{escape_html(org)}</p>'''
            link = vol.get("link")
            link_block = ""
            if isinstance(link, dict) and link.get("url") and link.get("text"):
                link_block = f'''                <br />
                <a href="{escape_html(link.get("url"))}" target="_blank" rel="noopener noreferrer" className="text-primary font-bold">{escape_html(link.get("text"))}</a>'''
            blocks.append(
                f'''              <div className="bg-card p-6 rounded-xl border-2 border-border shadow-lg">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-3">
                  <h3 className="text-xl font-semibold text-foreground">
                    {escape_html(vol.get("title",""))}
                  </h3>
                  <span className="text-primary font-medium">{escape_html(vol.get("period",""))}</span>
                </div>
                {org_block}
                <p className="text-foreground">
                  {escape_html(vol.get("description",""))}
                </p>
{link_block}
              </div>'''
            )
        inner = "\n\n".join(blocks)
        return f'''<section>
            <h2 className="text-3xl font-bold mb-6 text-primary border-b-2 border-primary pb-3 inline-block">
              VOLUNTEERING
            </h2>
            
            <div className="space-y-6">
{inner}
            </div>
          </section>'''

    def render_skill_array(items: List[Any]) -> str:
        return ", ".join([f"\"{escape_html(x)}\"" for x in (items or [])])

    technologies = skills.get("technologies", []) or []
    platforms = skills.get("platforms", []) or []
    soft = skills.get("soft", []) or []

    photo = personal.get("photo", "")
    title = personal.get("title", "")

    volunteering_section = render_volunteering()

    return f'''"use client"

import {{ useState, useEffect }} from "react"
import {{ {icons_import} }} from "lucide-react"

export default function Home() {{
  const [image, setImage] = useState<HTMLImageElement | null>(null)

  useEffect(() => {{
    const img = new Image()
    img.crossOrigin = "anonymous"
    img.onload = () => {{
      setImage(img)
    }}
    img.src = "/{photo}"
  }}, [])

  return (
    <main className="min-h-screen bg-background text-foreground relative overflow-hidden">
      <div className="fixed inset-0 pointer-events-none opacity-10">
        <div className="absolute top-0 left-0 w-96 h-96 bg-primary rounded-full blur-3xl"></div>
        <div className="absolute bottom-0 right-0 w-96 h-96 bg-primary rounded-full blur-3xl"></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-6 py-8 md:py-12">
        <header className="mb-16">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 lg:gap-12 items-center">
            <div className="order-2 lg:order-1 flex justify-center lg:justify-start">
              <div className="relative w-full max-w-lg aspect-4/3 rounded-2xl overflow-hidden border-4 border-primary shadow-2xl">
                {{image ? (
                    <img
                    src={{image.src}}
                    alt="Profile"
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full bg-card flex items-center justify-center">
                    <div className="text-muted-foreground">Loading...</div>
                  </div>
                )}}
              </div>
            </div>

            <div className="order-1 lg:order-2">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-4 text-foreground leading-tight">
                {escape_html(first_name).upper()}<br />{escape_html(last_name).upper()}
              </h1>
              <p className="text-xl md:text-2xl lg:text-3xl text-primary mb-8 font-medium">
                {escape_html(title)}
              </p>
              <div className="flex flex-wrap gap-4 text-sm md:text-base text-muted-foreground">
{render_links()}
              </div>
            </div>
          </div>
        </header>

        <div className="max-w-5xl mx-auto space-y-16">
          <section>
            <h2 className="text-3xl font-bold mb-6 text-primary border-b-2 border-primary pb-3 inline-block">
              SUMMARY
            </h2>
            <p className="text-foreground leading-relaxed text-lg whitespace-pre-line">
              {escape_html(summary)}
            </p>
          </section>

          <section>
            <h2 className="text-3xl font-bold mb-8 text-primary border-b-2 border-primary pb-3 inline-block">
              PROFESSIONAL EXPERIENCE
            </h2>
            
            <div className="space-y-10">
{render_experience()}
            </div>
          </section>

          <section>
            <h2 className="text-3xl font-bold mb-8 text-primary border-b-2 border-primary pb-3 inline-block">
              PROJECTS
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
{render_projects()}
            </div>
          </section>

{volunteering_section}

          <section>
            <h2 className="text-3xl font-bold mb-8 text-primary border-b-2 border-primary pb-3 inline-block">
              SKILLS
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-card p-6 rounded-xl border-2 border-border shadow-lg">
                <h3 className="font-semibold text-primary mb-4 text-lg">Technologies</h3>
                <div className="flex flex-wrap gap-2">
                  {{[{render_skill_array(technologies)}].map((skill) => (
                    <span
                      key={{skill}}
                      className="px-3 py-1.5 bg-primary/20 text-primary rounded-lg text-sm font-medium"
                    >
                      {{skill}}
                    </span>
                  ))}}
                </div>
              </div>
              
              <div className="bg-card p-6 rounded-xl border-2 border-border shadow-lg">
                <h3 className="font-semibold text-primary mb-4 text-lg">Platforms & Tools</h3>
                <div className="flex flex-wrap gap-2">
                  {{[{render_skill_array(platforms)}].map((skill) => (
                    <span
                      key={{skill}}
                      className="px-3 py-1.5 bg-primary/20 text-primary rounded-lg text-sm font-medium"
                    >
                      {{skill}}
                    </span>
                  ))}}
                </div>
              </div>
              
              <div className="bg-card p-6 rounded-xl border-2 border-border shadow-lg">
                <h3 className="font-semibold text-primary mb-4 text-lg">Soft Skills</h3>
                <div className="flex flex-wrap gap-2">
                  {{[{render_skill_array(soft)}].map((skill) => (
                    <span
                      key={{skill}}
                      className="px-3 py-1.5 bg-primary/20 text-primary rounded-lg text-sm font-medium"
                    >
                      {{skill}}
                    </span>
                  ))}}
                </div>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-3xl font-bold mb-8 text-primary border-b-2 border-primary pb-3 inline-block">
              EDUCATION
            </h2>
            
            <div className="space-y-6">
{chr(10).join([f'''              <div className="bg-card p-6 rounded-xl border-2 border-border shadow-lg">
                <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-2">
                  <h3 className="text-xl font-semibold text-foreground">
                    {escape_html(edu.get("degree",""))}
                  </h3>
                  <span className="text-primary font-medium">{escape_html(edu.get("period",""))}</span>
                </div>
                <p className="text-muted-foreground">{escape_html(edu.get("institution",""))}</p>
              </div>''' for edu in education])}
            </div>
          </section>

          <section className="pb-12">
            <h2 className="text-3xl font-bold mb-6 text-primary border-b-2 border-primary pb-3 inline-block">
              LANGUAGES
            </h2>
            
            <div className="bg-card p-6 rounded-xl border-2 border-border shadow-lg">
              <ul className="space-y-3 text-foreground list-none">
{chr(10).join([f'''                <li className="flex items-center gap-3">
                  <span className="text-primary text-xl">▸</span>
                  <span className="text-lg">{escape_html(lang)}</span>
                </li>''' for lang in languages])}
              </ul>
            </div>
          </section>
        </div>
      </div>
    </main>
  )
}}
'''

def generate_layout(resume: Dict[str, Any]) -> str:
    personal = resume.get("personal", {}) or {}
    fonts = resume.get("fonts", {}) or {}

    sans_font = fonts.get("sans") or "Geist"
    mono_font = fonts.get("mono") or "Geist Mono"

    sans_font_import = "_".join(str(sans_font).split())
    mono_font_import = "_".join(str(mono_font).split())

    sans_font_var = "_sans"
    mono_font_var = "_mono"

    return f'''import type React from "react"
import type {{ Metadata }} from "next"
import {{ {sans_font_import}, {mono_font_import} }} from "next/font/google"
import "./globals.css"

const {sans_font_var} = {sans_font_import}({{ subsets: ["latin"] }})
const {mono_font_var} = {mono_font_import}({{ subsets: ["latin"] }})

export const metadata: Metadata = {{
  title: "{escape_html(personal.get("name",""))}",
  description: "Resume Website",
}}

export default function RootLayout({{
  children,
}}: Readonly<{{
  children: React.ReactNode
}}>) {{
  return (
    <html lang="en">
      <body className={{`font-sans antialiased`}}>
        {{children}}
      </body>
    </html>
  )
}}
'''


def generate_globals_css(resume: Dict[str, Any]) -> str:
    colors = resume.get("colors", {}) or {}
    fonts = resume.get("fonts", {}) or {}

    sans = fonts.get("sans") or "Geist"
    mono = fonts.get("mono") or "Geist Mono"

    def c(key: str, default: str) -> str:
        val = colors.get(key)
        return str(val) if val else default

    return f'''@import "tailwindcss";
@import "tw-animate-css";

@custom-variant dark (&:is(.dark *));

:root {{
  --background: {c("background", "#020202")};
  --foreground: {c("foreground", "#CECFC7")};
  --card: {c("card", "#1a1a1a")};
  --card-foreground: {c("cardForeground", "#CECFC7")};
  --popover: {c("popover", "#1a1a1a")};
  --popover-foreground: {c("popoverForeground", "#CECFC7")};
  --primary: {c("primary", "#3E6259")};
  --primary-foreground: {c("primaryForeground", "#CECFC7")};
  --secondary: {c("secondary", "#2a2a2a")};
  --secondary-foreground: {c("secondaryForeground", "#CECFC7")};
  --muted: {c("muted", "#2a2a2a")};
  --muted-foreground: {c("mutedForeground", "#9a9a9a")};
  --accent: {c("accent", "#3E6259")};
  --accent-foreground: {c("accentForeground", "#CECFC7")};
  --destructive: {c("destructive", "#dc2626")};
  --destructive-foreground: {c("destructiveForeground", "#CECFC7")};
  --border: {c("border", "#3E6259")};
  --input: {c("input", "#2a2a2a")};
  --ring: {c("ring", "#3E6259")};
  --chart-1: {c("chart1", "#3E6259")};
  --chart-2: {c("chart2", "#CECFC7")};
  --chart-3: {c("chart3", "#5a7a72")};
  --chart-4: {c("chart4", "#8a9a94")};
  --chart-5: {c("chart5", "#a0b0aa")};
  --radius: 0.5rem;
  --sidebar: {c("card", "#1a1a1a")};
  --sidebar-foreground: {c("foreground", "#CECFC7")};
  --sidebar-primary: {c("primary", "#3E6259")};
  --sidebar-primary-foreground: {c("primaryForeground", "#CECFC7")};
  --sidebar-accent: {c("secondary", "#2a2a2a")};
  --sidebar-accent-foreground: {c("secondaryForeground", "#CECFC7")};
  --sidebar-border: {c("border", "#3E6259")};
  --sidebar-ring: {c("ring", "#3E6259")};
}}

.dark {{
  --background: {c("background", "#020202")};
  --foreground: {c("foreground", "#CECFC7")};
  --card: {c("card", "#1a1a1a")};
  --card-foreground: {c("cardForeground", "#CECFC7")};
  --popover: {c("popover", "#1a1a1a")};
  --popover-foreground: {c("popoverForeground", "#CECFC7")};
  --primary: {c("primary", "#3E6259")};
  --primary-foreground: {c("primaryForeground", "#CECFC7")};
  --secondary: {c("secondary", "#2a2a2a")};
  --secondary-foreground: {c("secondaryForeground", "#CECFC7")};
  --muted: {c("muted", "#2a2a2a")};
  --muted-foreground: {c("mutedForeground", "#9a9a9a")};
  --accent: {c("accent", "#3E6259")};
  --accent-foreground: {c("accentForeground", "#CECFC7")};
  --destructive: {c("destructive", "#dc2626")};
  --destructive-foreground: {c("destructiveForeground", "#CECFC7")};
  --border: {c("border", "#3E6259")};
  --input: {c("input", "#2a2a2a")};
  --ring: {c("ring", "#3E6259")};
  --chart-1: {c("chart1", "#3E6259")};
  --chart-2: {c("chart2", "#CECFC7")};
  --chart-3: {c("chart3", "#5a7a72")};
  --chart-4: {c("chart4", "#8a9a94")};
  --chart-5: {c("chart5", "#a0b0aa")};
  --sidebar: {c("card", "#1a1a1a")};
  --sidebar-foreground: {c("foreground", "#CECFC7")};
  --sidebar-primary: {c("primary", "#3E6259")};
  --sidebar-primary-foreground: {c("primaryForeground", "#CECFC7")};
  --sidebar-accent: {c("secondary", "#2a2a2a")};
  --sidebar-accent-foreground: {c("secondaryForeground", "#CECFC7")};
  --sidebar-border: {c("border", "#3E6259")};
  --sidebar-ring: {c("ring", "#3E6259")};
}}

@theme inline {{
  --font-sans: "{sans}", "{sans} Fallback";
  --font-mono: "{mono}", "{mono} Fallback";
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-card: var(--card);
  --color-card-foreground: var(--card-foreground);
  --color-popover: var(--popover);
  --color-popover-foreground: var(--popover-foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-secondary: var(--secondary);
  --color-secondary-foreground: var(--secondary-foreground);
  --color-muted: var(--muted);
  --color-muted-foreground: var(--muted-foreground);
  --color-accent: var(--accent);
  --color-accent-foreground: var(--accent-foreground);
  --color-destructive: var(--destructive);
  --color-destructive-foreground: var(--destructive-foreground);
  --color-border: var(--border);
  --color-input: var(--input);
  --color-ring: var(--ring);
  --color-chart-1: var(--chart-1);
  --color-chart-2: var(--chart-2);
  --color-chart-3: var(--chart-3);
  --color-chart-4: var(--chart-4);
  --color-chart-5: var(--chart-5);
  --radius-sm: calc(var(--radius) - 4px);
  --radius-md: calc(var(--radius) - 2px);
  --radius-lg: var(--radius);
  --radius-xl: calc(var(--radius) + 4px);
  --color-sidebar: var(--sidebar);
  --color-sidebar-foreground: var(--sidebar-foreground);
  --color-sidebar-primary: var(--sidebar-primary);
  --color-sidebar-primary-foreground: var(--sidebar-primary-foreground);
  --color-sidebar-accent: var(--sidebar-accent);
  --color-sidebar-accent-foreground: var(--sidebar-accent-foreground);
  --color-sidebar-border: var(--sidebar-border);
  --color-sidebar-ring: var(--sidebar-ring);
}}

@layer base {{
  * {{
    @apply border-border outline-ring/50;
  }}
  body {{
    @apply bg-background text-foreground;
  }}
}}
'''


def main() -> None:
    repo_root = Path(os.getcwd())
    resume_yaml_path = repo_root / "resume.yaml"
    app_dir = repo_root / "app"

    if not resume_yaml_path.exists():
        print("Error: resume.yaml not found!", file=sys.stderr)
        print("Please copy resume.example.yaml to resume.yaml and customize it.", file=sys.stderr)
        raise SystemExit(1)

    try:
        resume_yaml = resume_yaml_path.read_text(encoding="utf-8")
        resume = yaml.safe_load(resume_yaml) or {}

        app_dir.mkdir(parents=True, exist_ok=True)

        page_content = generate_page(resume)
        layout_content = generate_layout(resume)
        css_content = generate_globals_css(resume)

        (app_dir / "page.tsx").write_text(page_content, encoding="utf-8")
        (app_dir / "layout.tsx").write_text(layout_content, encoding="utf-8")
        (app_dir / "globals.css").write_text(css_content, encoding="utf-8")

        print("✓ Generated app/page.tsx")
        print("✓ Generated app/layout.tsx")
        print("✓ Generated app/globals.css")
        print("\n✓ Generation complete!")

    except Exception as e:
        print(f"Error generating site: {e}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
