# CUDA-Q Academic


> **🚀 Start Your Journey Here**
>
> * Visit the **[CUDA-Q Academic Learning Paths](https://nvidia.github.io/cuda-q-academic/learningpath.html)** to launch the modules and build a custom curriculum.
> * Browse the **[CUDA-Q Academic Visualization Gallery](https://nvidia.github.io/cuda-q-academic/visualization-gallery.html)** to experiment with the interactive tools featured in the lessons.
> * **Stay Connected:** [Sign up for the CUDA-Q newsletter](https://www.nvidia.com/en-us/solutions/quantum-computing/cuda-q-newsletter/) to get updates on tutorials, releases, and events.


## About


NVIDIA's [CUDA-Q Academic](https://developer.nvidia.com/blog/transforming-quantum-education-with-ai-supercomputing-and-nvidia-cuda-q-academic/) is a freely available, open-source collection of interactive educational resources that prepare the next generation of quantum computing professionals by combining high-performance computing with quantum computing. Designed to supplement university quantum computing courses, it enriches classroom instruction and textbook learning with hands-on, interactive modules built using [CUDA-Q](https://developer.nvidia.com/cuda-q), NVIDIA's open-source platform for hybrid classical-quantum computing. Developed by NVIDIA in collaboration with universities and tested in real classroom settings, CUDA-Q Academic is organized in modules with topics ranging from a Quick Start to Quantum Computing through Quantum Error Correction, Quantum Algorithm Simulation 101, Dynamics 101, AI for Quantum, Chemistry Simulations, and more. Materials are free to use for educational purposes under Apache-2.0 and CC-BY-NC-4.0; see [LICENSE](LICENSE).



## Quick Links

| Resource | Link |
|---|---|
| Learning Paths (launch modules, build a curriculum) | https://nvidia.github.io/cuda-q-academic/learningpath.html |
| Visualization Gallery (interactive widgets) | https://nvidia.github.io/cuda-q-academic/visualization-gallery.html |
| CUDA-Q Newsletter (updates, tutorials, events) | https://www.nvidia.com/en-us/solutions/quantum-computing/cuda-q-newsletter/ |
| Machine-readable curriculum catalog | [curriculum.json](curriculum.json) |
| Guide to CUDA-Q Backends | [Guide-to-cuda-q-backends.ipynb](Guide-to-cuda-q-backends.ipynb) |
| Instructor Guide | [Instructor-Guide.md](Instructor-Guide.md) |
| Contributing | [CONTRIBUTING.md](CONTRIBUTING.md) |
| Install CUDA-Q | https://nvidia.github.io/cuda-quantum/latest/using/quick_start.html |


<details>
<summary>Coming from another quantum framework?</summary>

The [CUDA-Q Hello World visualization](https://nvidia.github.io/cuda-q-academic/quick-start-to-quantum/interactive_widget/cudaq-hello-world.html) shows how a quantum circuit diagram translates into CUDA-Q code — a good starting point before you open your first notebook.

</details>


## Repository Contents

The repository is organized into the learning path modules below. For machine-readable lesson and widget discovery, use [curriculum.json](curriculum.json). For hosted module overviews, prerequisites, and a curriculum builder, visit the [Learning Paths](https://nvidia.github.io/cuda-q-academic/learningpath.html) page.

| Module | Folder | Topic |
|---|---|---|
| Quick Start to Quantum Computing | [quick-start-to-quantum/](quick-start-to-quantum/) | From zero to a variational algorithm in CUDA-Q |
| Quantum Algorithm Simulation 101 | [simulation/](simulation/) | Choosing between state vector, tensor network, MPS, Pauli propagation, and stabilizer simulation |
| Quantum Information Science Examples | [qis-examples/](qis-examples/) | Foundational quantum algorithms to complement QIS courses |
| Quantum Error Correction 101 | [qec101/](qec101/) | Classical and quantum codes, decoders, magic-state distillation |
| Chemistry Simulations | [chemistry-simulations/](chemistry-simulations/) | VQE, ADAPT-VQE, QM/MM, Krylov methods, and more.
| Quantum Applications for Finance | [quantum-applications-to-finance/](quantum-applications-to-finance/) | Quantum walks, portfolio optimization, QChop |
| QAOA for Max Cut | [qaoa-for-max-cut/](qaoa-for-max-cut/) | Divide-and-conquer QAOA with circuit cutting |
| AI for Quantum | [ai-for-quantum/](ai-for-quantum/) | Using AI models to enable quantum computing |
| Dynamics 101 | [dynamics101/](dynamics101/) | GPU-accelerated Schrödinger and Lindblad time evolution |
| Hybrid Workflows | [hybrid-workflows/](hybrid-workflows/) | Hybrid classical–quantum workflow examples |

Each module folder contains student notebooks, a module-local `README.md`, a `solutions/` subfolder, and an `images/` subfolder with figures.

### Instructor Resources

| Resource | Folder | Description |
|---|---|---|
| Quantum Computing Group Project | [quantum-ai-project-template/](quantum-ai-project-template/) | Role-based, agentic-AI group project template for deploying a quantum-GPU computing project in a course. See the [Group Project](#quantum-computing-group-project) section below. |
| Calibration | [calibration/](calibration/) | Classroom guide for using [NVIDIA's Ising Calibration](https://build.nvidia.com/nvidia/ising-calibration-1-35b-a3b) — an open vision-language model purpose-built for quantum hardware calibration plot analysis. Browser-based NIM playground (no setup, no API key) plus sample plots from the [QCalEval dataset](https://huggingface.co/datasets/nvidia/QCalEval). Hands-on tutorial notebooks coming soon. |


## Quantum Computing Group Project

The CUDA-Q Academic Quantum Computing Group Project is a course-ready template for running a hybrid quantum-GPU computing project as a team assignment. It is designed around **agentic AI**: each student takes one of four defined roles — Project Lead, Performance Optimization, Quality Assurance, and Technical Marketing — and configures an AI coding agent (Claude Code, Cursor, Windsurf, or any chat-based LLM) from a role-specific starter prompt. Students retain accountability for architecture, classical benchmarking, and honest reporting while delegating implementation to their agents.

Teams (or solo students taking all roles sequentially) move through four milestones — plan, research, build, and showcase — with explicit deliverables at each step. The template ships with:

- Faculty guides, student-facing templates, and role cards
- Starter system prompts for each role and the CUDA-Q skill install
- A deliverable template that captures the plan, benchmark results, and individual retrospectives
- Suggested project options ranging from a fully scaffolded problem (the MIT iQuHACK 2026 LABS challenge) to student-designed projects

It is not a self-paced module. See [quantum-ai-project-template/Teaching-Guide.md](quantum-ai-project-template/Teaching-Guide.md) for deployment instructions and the [folder README](quantum-ai-project-template/README.md) for the file inventory.


## How to Run

> **Recommended: launch on NVIDIA Brev.** Brev provisions a pre-built CPU or GPU instance with CUDA-Q and all notebook prerequisites already installed. 
>
> **Launch: https://brev.nvidia.com/launchable/deploy/now?launchableID=env-39dN1v7RucHHgj97LILUlnXjnk5**
>
> See [brev-instructions.pdf](brev-instructions.pdf) for a step-by-step walkthrough.

Other entry points:

- **qBraid** — hosted Jupyter environment with CUDA-Q support. Visit [qbraid.com](https://www.qbraid.com/).
- **Amazon Braket** — managed quantum development environment that can run CUDA-Q notebooks in Jupyter.
- **Google Colab** — each notebook includes a commented-out install cell. Uncomment it, run it to install CUDA-Q and download supporting assets, restart the kernel, and run the notebook.
- **Local** — install CUDA-Q directly following the [CUDA-Q install guide](https://nvidia.github.io/cuda-quantum/latest/using/quick_start.html#install-cuda-q). Recommended for the largest GPU-accelerated examples.

Each module's `README.md` contains module-specific run notes.


## Contributing

New notebook content follows the schema defined by [notebook_template.ipynb](notebook_template.ipynb): the first markdown cell contains the title plus labeled sections for **What You Will Do**, **Prerequisites**, **Key Terminology**, **CUDA-Q Syntax**, and a **Solutions** link. Agents and tooling can rely on this schema to programmatically discover what each notebook covers. AI coding agents working in this repository should read [AGENTS.md](AGENTS.md) first.


## License & Attribution

CUDA-Q Academic is released under [Apache-2.0 and CC-BY-NC-4.0](LICENSE). Developed by NVIDIA in collaboration with university partners; freely available for educational use. This project downloads and installs additional third-party open-source software; review the licenses of those projects before use.
