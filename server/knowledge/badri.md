# Badri's background

## Summary
Full-Stack Software Engineer in the San Francisco Bay Area with 4+ years building and operating end-to-end systems: React/TypeScript and Vue front ends; Java/Spring Boot, Python/FastAPI and Node.js back ends; React Native mobile; and distributed services on AWS. Ships production GenAI (LLMs, RAG, multi-agent orchestration, evals, MCP) and builds agent platforms with sandboxed execution, telemetry and regression-gated releases. At Zoho, built finance software across Books, Expense and Payroll (the Expense–Payroll integration won 100+ new customers) and cut production incidents 30%; built subscription billing at Wipro; held 99%+ uptime on-call at Panasia, owning CI/CD, telemetry and safe rollouts end to end. Works Agile with designers, product and backend engineers. **Open to Software Engineer (SDE), Full-Stack Engineer and GenAI Engineer roles.**

## About me
- Name: Badri Rajendran. Based in the San Francisco Bay Area, CA.
- I care about the unglamorous parts of AI features: observability, cost tracking, test coverage and on-call. That's the line between an AI feature that demos well and one people can lean on.
- I think in systems first: map the structure, stress-test it, then ship.
- What I'm good at: designing agentic systems that stay reliable, observable and cost-aware in production; full product lifecycle ownership, from API and schema design through CI/CD, deployment and on-call; bridging classic backend engineering (Java/Spring, Python) with modern GenAI tooling.
- Right now: I'm a GenAI Engineer Intern at Presenter Prep, I'm building PolicyPal, and I'm going deep on LLM evaluation and agent observability at scale.

## Experience (most recent first)

### GenAI Engineer Intern, Presenter Prep (Mountain View, CA), July 2026 – Present
- Built an LLM-as-Judge eval harness that rates Gemini 2.5 Flash native-audio responses, making output quality measurable instead of anecdotal.
- Engineering an end-to-end RAG chatbot (document retrieval, context assembly and tool calling) so answers stay grounded in real source material.
- Shipping full-stack features across a React/TypeScript frontend and a serverless backend deployed on Cloudflare.

### GenAI Engineer Intern, Panasia Estate Inc. (New York, USA), Sept 2025 – Mar 2026
- Shipped a Claude-powered RAG pipeline (chunking, embeddings, vector search) for automated document parsing, cutting processing time ~50%.
- Instrumented LLM serving with latency tracing and per-request cost telemetry to surface bottlenecks and control spend.
- Deployed GenAI features into a client-facing platform (React/TypeScript, Java/Spring Boot, Python/FastAPI), tuning API latency ~35%.
- Owned production reliability (GitHub Actions CI/CD, Dockerized EKS, CloudWatch on-call), sustaining 99%+ uptime.
- Iterated prompt engineering and retrieval parameters against evals to improve RAG accuracy and reduce hallucinations.

### Software Developer Intern, MarlnCorp (California, USA), Feb 2025 – June 2025
- Shipped a production LMS web app in React/TailwindCSS on tight agile cycles with responsive, mobile-first layouts.
- Architected a fault-tolerant AWS deployment (EC2, EKS) with auto-scaling and load balancing, cutting infrastructure cost ~30%.
- Built a reusable React component library and design system to standardize UI and speed up feature work.
- Designed REST APIs and PostgreSQL schemas with JWT auth and role-based access control.

### Software Developer, Wipro (Bengaluru, IN), Aug 2023 – July 2024
- Delivered full-stack features across React frontends and Python/Flask/Django backends, raising PyTest coverage ~10%.
- Built Kotlin Android and React Native apps on Flask/Django APIs, with OAuth, batched jobs and templated PDF generation.
- Integrated Razorpay one-time and recurring subscription payments, with user-role and invitation management.
- Contributed end-to-end to the company website build, helping bring 200+ customers onboard.
- Added Redis caching to cut database load and page latency on high-traffic pages.

### Software Engineer, Zoho Corporation (Chennai, IN), Aug 2021 – July 2023
- Built the Zoho Expense–Payroll integration in Java and Spring Boot, acquiring 100+ new Payroll customers.
- Led setup of the Continuous Integration system for the Zoho Books repository with GitLab CI/CD.
- Cut recurring production incidents ~30% by root-causing abnormalities and coordinating timely fixes across teams.
- Designed feature flags and rollout safeguards to deploy integration changes incrementally without disrupting customers.
- Tuned query execution and concurrency for high-load Payroll operations, improving throughput and reducing contention.
- Conducted code reviews and design discussions across Zoho Finance suite microservices, upholding code quality.
- Developed SQL integrity queries to monitor and fix database integrity issues across production datasets.
- Refactored legacy Java/Spring Boot modules with added unit tests, reducing production defects and tech debt.
- Built internal scripts to automate routine integration and data-validation tasks, reducing manual effort.

## Projects

### PolicyPal (my flagship project, in progress): https://github.com/Badri-Rajendran/PolicyPal
A grounded RAG assistant that answers insurance questions (health, auto, life, home and more) from a curated Wikipedia + HealthCare.gov knowledge base. Every answer cites its sources, and it refuses questions it can't ground instead of guessing.
- Hybrid retrieval: BM25 plus pgvector semantic search, reranked by a cross-encoder and filtered by a relevance threshold; every answer lists its source passages and relevance scores, and citations persist when a conversation is reopened.
- Ingestion pipeline: fetch → normalize → chunk → embed → store in pgvector, reproducible end to end.
- Embeddings (bge-small-en-v1.5) and reranking (ms-marco-MiniLM-L-6-v2) run locally on open-source Hugging Face models; answers are generated by an OpenAI hosted model.
- Eval-driven: retrieval and generation evals with regression floors. Adding the HealthCare.gov corpus cut unanswered test questions from 12/20 to 4/20, and advice-shaped questions are refused by design.
- Threaded conversations with follow-up questions rewritten into standalone questions before retrieval.
- Guardrails: JWT-authenticated API with per-user thread isolation and a per-user daily token budget. CI runs linting, a migration drift check, SAST, dependency audits, secret scanning and an 85% backend test-coverage floor. Architectural decisions are recorded in 11 ADRs.
- Stack: React 19 (Vite), Flask, PostgreSQL + pgvector, SQLAlchemy + Alembic, rank-bm25, sentence-transformers, Hugging Face transformers, OpenAI.
- In progress: comparison of ACA individual and family health plans from the CMS Marketplace API, by ZIP code and age through a tool call, priced live for the 30 HealthCare.gov states. It compares plans and never recommends one. Next: ingesting Summary of Benefits and Coverage (SBC) documents.

### CodeSage: Agentic Code Review Assistant (Mar 2026, completed): https://github.com/Badri-Rajendran/CodeSage
A Claude-powered multi-agent system that reviews pull requests the way a senior team would, reasoning, reflecting and citing codebase context before it comments.
- Multi-agent PR review on LangGraph (ReAct + self-reflection), cutting review turnaround ~40%.
- A pgvector RAG pipeline on PostgreSQL and an LLM-as-Judge eval harness with cross-version regression detection.
- Parallel security, correctness and style reviewer agents with sandboxed tests and human-in-the-loop gates.
- Containerized on AWS (Lambda + ECS) with token-cost telemetry; agents exposed over REST and an MCP server.
- Stack: Python, FastAPI, LangGraph, LangChain, Claude API, pgvector, PostgreSQL, MCP, AWS, Docker.

### Trueup: https://github.com/Badri-Rajendran/Trueup
A regulated retail-investing platform (USD, US-listed equities and bonds). Customers pass identity verification, link a bank to deposit funds, invest in one of four model portfolios with T+1 settlement, and get monthly automatic rebalancing.
- Immutable double-entry accounting for every transaction, tax-lot tracking for every purchase, restatable returns.
- Integrations: Stripe Identity and Stripe Billing (fees), Plaid bank linking, Alpaca paper trading. Most integrations are adapters tested against fakes; Stripe Billing is verified against the real sandbox.
- Stack: Python 3.12, Flask, SQLAlchemy 2, PostgreSQL 16 with Alembic, React, Redis, Docker/Docker Compose, GitHub Actions, Azure Container Apps.
- Specified up front: architecture specs, 48 functional and 18 non-functional requirements, and a decision log.

### Lifeline (JacHacks SF, July 26, 2026): https://devpost.com/software/lifeline-a7t6qe
A hackathon project that uses Jac's graph-native AI to verify crisis reports, predict cascading failures and recommend emergency resource allocation in real time. It models disasters as graphs of people, locations, infrastructure, resources and events.
- My role: the frontend, including the Cytoscape graph dashboard, the demo engine and the landing page. Built with teammates Sai Shiva Satwik Mallajosyula (backend and Jac) and Mohammed Khabaza (architecture).
- Stack: Jac, FastAPI, MongoDB, Next.js + React, Python, TypeScript. Team repo: https://github.com/amirkhabaza/JacHacks2026

### Autonomous-SRE: https://github.com/Badri-Rajendran/Autonomous-SRE
A self-healing incident agent built to cut MTTR and burnout: it detects errors, researches root causes across the codebase and the web, generates patches, and loops in a human by voice (Bland AI) for sign-off. Language: JavaScript.

### NYC Real Estate Intelligence (May 2026): https://github.com/Badri-Rajendran/NYC-Real-Estate-Intelligence
An end-to-end ML pipeline that classifies NYC properties as undervalued, fair or overvalued using five public civic APIs, including Census, NYPD, NYC DOE and Walk Score. Includes an XGBoost feature-engineering pipeline, a hybrid recommender, and a Claude conversational agent for natural-language queries. Stack: Python, scikit-learn, XGBoost, SoQL, Claude.

### NYC Capital Budget Explorer: https://github.com/Badri-Rajendran/NYC_Capital_Budget_Explorer
A civic-transparency web platform that visualizes daily-updated city budget data and folds in user feedback, to foster accountability in government spending. Language: JavaScript.

### LMS Learning Platform (MarlnCorp): https://github.com/MarlnCorp-ai/LMS-React-App
A modern Learning Management System frontend in React and TailwindCSS, with course management, enrollment, progress tracking and quizzes, shipped from prototype to production.

## Skills
- Generative AI: Claude API, Gemini API, OpenAI API, LangChain, LangGraph, RAG, hybrid retrieval (BM25 + vector), cross-encoder reranking, multi-agent orchestration, MCP servers, embeddings and vector search, sentence-transformers, LLM-as-Judge evals, tool calling, prompt engineering, fine-tuning, Hugging Face.
- Languages: Java, Python, TypeScript, JavaScript, Kotlin, SQL, HTML, CSS.
- Frameworks: React, Redux, Vue, Angular, Next.js, Vite, Node.js, Express, Spring Boot, FastAPI, Flask, Django, TailwindCSS, JUnit, PyTest, Selenium.
- Mobile: Android (Kotlin), React Native, hybrid mobile apps, REST API integration.
- Data and ML: Pandas, NumPy, SciPy, scikit-learn, XGBoost, PyTorch, TensorFlow, Transformers, Matplotlib, Seaborn.
- Cloud: AWS (EC2, Lambda, S3, RDS, EKS, ECS, Fargate, API Gateway, CloudFormation, CloudWatch, SQS, SNS, IAM, VPC, Secrets Manager), Azure Container Apps, Cloudflare, serverless.
- Databases: PostgreSQL, MySQL, MongoDB, DynamoDB, Redis, pgvector, SQLAlchemy, Alembic.
- DevOps and tools: Docker, Kubernetes, Helm, Terraform, Jenkins, Ansible, GitHub Actions, GitLab CI/CD, Prometheus, Grafana, Git, Maven, Gradle, Postman, Linux (Ubuntu, Debian), Unix, macOS, Windows, Bash, SSH, cron, apt/npm/pip/uv.
- Architecture, practices and integrations: microservices, REST APIs, distributed systems, event-driven architecture, system design, test-driven development, Agile/Scrum, OOP, OAuth/JWT, data structures and algorithms; payment and fintech APIs: Stripe (Billing, Identity), Plaid, Alpaca, Razorpay.

## Education
- M.S. in Computer Science, Stevens Institute of Technology, Hoboken, NJ, Aug 2024 – May 2026. Coursework: ML & Neural Networks, Data Mining, Distributed Systems, Software Architecture, Object-Oriented Design, Deep Learning, DevOps, Natural Language Processing, DBMS, Cloud Computing.
- B.E. in Computer Science, Anna University, Chennai, IN, Aug 2018 – May 2022.

## Profiles and contact
- Email: badriathindran@gmail.com
- Phone: +1 201-687-9279
- LinkedIn: https://www.linkedin.com/in/badri-rajendran/
- GitHub: https://github.com/Badri-Rajendran (achievements: Pull Shark ×2, Quickdraw, YOLO)
- X / Twitter: https://x.com/badhrirajen
- YouTube: https://youtube.com/@BadriRajendran
- LeetCode: https://leetcode.com/u/badhri_rajendran/
- Codeforces: https://codeforces.com/profile/badhrirajen
- Résumé: https://badri-rajendran.github.io/BadriRajendran_Resume.pdf
- Portfolio: https://badri-rajendran.github.io
