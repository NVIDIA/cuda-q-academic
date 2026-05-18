# Quantum AI Project Template

**Instructor resource.** A role-based group project template for deploying a hands-on quantum–GPU computing capstone in your course. Students work in teams of four — each owning a distinct technical role — and move through four project milestones with AI coding agents as a working peer.

The template is a complete project scaffold: a teaching guide, student guide, deliverable template, role cards, and AI agent prompts. Customize the problem and the compute environment to fit your course; everything else is ready to distribute.

---

## How it works

**Student roles** *(one per team member)*

* **Project Lead** — coordinates the team, owns the project plan and integration.
* **Performance Optimization PIC** — profiles, scales, and accelerates the workflow on GPU and (where available) QPU backends.
* **Quality Assurance PIC** — designs validation, writes tests, and verifies correctness against classical or simulated references.
* **Technical Marketing PIC** — explains the project to a technical-but-non-expert audience and produces the final write-up.

**Four milestones** structure the project from problem framing to final deliverable. Each milestone has clear handoffs in `deliverable-template.md`, and each role has a dedicated role card describing what to focus on at each stage.

**AI agents** are wired into the workflow as a peer the team can delegate to — for code generation, performance analysis, test design, and writing. Configurations and prompts are provided.

---

## What it's for

Adopt the template when you want a structured group project that:

* Exercises CUDA-Q and hybrid quantum–GPU workflows at the level of a course final project.
* Gives every team member a clear, technical, gradeable role.
* Demonstrates working alongside AI agents as a productive engineering practice.
* Slots into a semester-long or intensive (1–2 week) course schedule with minimal instructor lift.

---

## What's in this folder

### Faculty guides *(ready to use)*

| File | Purpose |
| :--- | :--- |
| `Teaching-Guide.md` | How to deploy the project: what to customize, timing, assessment, common questions. **Start here.** |

### Student-facing templates *(complete — customize before distributing)*

These files are templates. Before distributing them to students, fill in the course-specific details described in `Teaching-Guide.md` → "Before You Deploy": your project problem, available tools and compute, and submission instructions.

| File | What it is |
| :--- | :--- |
| `quantum-group-project-guide.md` | Main student guide: roles, milestones, rubric, environment setup. |
| `deliverable-template.md` | The document student teams fill in across all four project milestones. |
| `role-cards/role-card-project-lead.md` | Role card for the Project Lead. |
| `role-cards/role-card-performance-optimization.md` | Role card for the Performance Optimization PIC. |
| `role-cards/role-card-quality-assurance.md` | Role card for the Quality Assurance PIC. |
| `role-cards/role-card-technical-marketing.md` | Role card for the Technical Marketing PIC. |

---

## Before distributing to students

Complete the checklist in **`Teaching-Guide.md` → "Before You Deploy"**. The three required steps are:

1. **Choose or provide the project problem** — pick one of the suggested projects (Options A–D), let students design their own (Option E), or add your own course-specific problem.
2. **Tell students what tools and compute they have** — specify which AI assistant and which execution environments (CPU, GPU, QPU) are available in your course.
3. **Add submission instructions and customize the rubric** — the template rubric is a starting point; adapt it to your course and the specific problem you've assigned.

---

*Developed for [NVIDIA CUDA-Q Academic](https://github.com/NVIDIA/cuda-q-academic). Adaptation and reuse with attribution encouraged.*
