# Badri's background

## Summary
Full-Stack Software Engineer in the San Francisco Bay Area with 4+ years building and operating end-to-end systems: React/TypeScript and Vue front ends; Java/Spring Boot, Python/FastAPI and Node.js back ends; React Native mobile; and distributed services on AWS. Ships production GenAI (LLMs, RAG, multi-agent orchestration, evals, MCP) and builds agent platforms with sandboxed execution, telemetry and regression-gated releases. Works Agile with designers, product and backend engineers. The 4+ years are three years continuous full-time at Zoho and Wipro (Aug 2021 – July 2024), plus about 18 months of internship work at MarlnCorp, Panasia and Presenter Prep alongside my M.S. **Open to Software Engineer (SDE), Full-Stack Engineer, Backend Engineer, Frontend Engineer, Cross-Platform Developer, GenAI Engineer, Forward Deployed Engineer roles.**

## About me
- Name: Badri Rajendran.
- I care about the unglamorous parts of AI features: observability, cost tracking, test coverage and on-call. That's the line between an AI feature that demos well and one people can lean on.
- I think in systems first: map the structure, stress-test it, then ship.
- What I'm good at: designing agentic systems that stay reliable in production using LangChain and LangGraph; full product lifecycle ownership, from API and schema design through CI/CD, deployment and on-call; bridging classic backend engineering (Java/Spring, Python) with modern GenAI tooling.
- Right now: I'm a GenAI Engineer Intern at Presenter Prep, I'm building PolicyPal, and I'm going deep on LLM evaluation and agent observability using LangFuse at scale.

## Experience (most recent first)

### GenAI Engineer Intern, Presenter Prep (Mountain View, CA), July 2026 – Present
- Built an LLM-as-Judge eval harness that rates Gemini 2.5 Flash native-audio responses, plus evals for the mock-interview system prompts, making output quality measurable instead of anecdotal.
- Built AI Interview Mode on the Gemini Live API (gemini-2.5-flash-native-audio): questions are read aloud and answered by voice, with a 10-second advance countdown that resets when the candidate resumes speaking, Done/Next to finish early, and a walk-away safeguard that ends the session after two silent questions.
- Split interview scoring so the measurable half is reproducible: filler words, words-per-minute and pauses are computed in code, while PREP and STAR rubric scores come back as Gemini structured output — the same recording always produces the same numbers.
- Delivered an end-to-end AI video processing system for Santa Clara University in time for their demo day, giving founders feedback on pitch delivery, tone and pace.
- Shipping full-stack features across a React/TypeScript frontend and Python FastAPI backend deployed on Cloudflare, working from requirements gathered in 10+ direct user interviews.

### GenAI Engineer Intern, Panasia Estate Inc. (New York, USA), Sept 2025 – Mar 2026
GenAI engineering for a client-facing real-estate platform: taking LLM-based solutions into a live business application and keeping them running.
- Shipped a Claude-powered RAG pipeline (chunking, embeddings, vector search) for automated document parsing, cutting processing time ~50%.
- Instrumented LLM serving with latency tracing and per-request cost telemetry to surface bottlenecks and control spend.
- Built scalable Python/FastAPI services behind the platform, tuning API latency ~35%, and the React/TypeScript interfaces on those REST endpoints through to PostgreSQL.
- Owned production reliability (GitHub Actions CI/CD, Dockerized EKS, CloudWatch on-call), sustaining 99%+ uptime.
- Iterated prompt engineering and retrieval parameters against evals to improve RAG accuracy and reduce hallucinations.

### Software Developer Intern, MarlnCorp (Cupertino, CA), Feb 2025 – June 2025
- Led a team of 5 to ship a production LMS end to end, demoing v1 to enterprise clients in the UAE and Saudi Arabia.
- Shipped the LMS front end in React/TailwindCSS on one-week agile cycles with responsive, mobile-first layouts built from UI/UX designs.
- Built Java/Spring Boot REST API services on PostgreSQL with JWT auth and role-based access control, powering that front end.
- Tuned transaction isolation to cut lock contention on the database.
- Architected a fault-tolerant AWS deployment (EC2, EKS) with auto-scaling and load balancing, cutting infrastructure cost ~30%.
- Built a reusable React component library and design system to standardize UI and speed up feature work.

### Software Developer, Wipro (Bengaluru, IN), Aug 2023 – July 2024
- Delivered full-stack features across React frontends and Python/Django backends, raising PyTest coverage ~10%.
- Built hybrid React Native apps for Android and iOS on Django APIs, with OAuth, scheduled batch jobs and templated PDF generation.
- Made those apps work on bad connections: an offline-first SQLite cache shown first and synced when connectivity returns, virtualized lists for long scrolling, and app-lifecycle handling that persists state before the OS kills a backgrounded app and resyncs on return.
- Kept mobile battery and data use low with debouncing and rate limiting on calls to the server, and handled safe-area alignment and orientation changes across both platforms.
- Built React interfaces on Django REST endpoints with server-side pagination, filtering and role-gated views.
- Integrated Razorpay one-time and recurring subscription payments, with user-role, permission and invitation management.
- Contributed end-to-end to the company website build, helping bring 200+ customers onboard.
- Added Redis caching to cut database load and page latency on high-traffic pages.
- Built a Jenkins pipeline running CI tests and deploying containers to a container registry and EC2 instances.

### Software Engineer, Zoho Corporation (Chennai, IN), Aug 2021 – July 2023
- Built the Zoho Expense–Payroll integration end to end in Java and Spring Boot, acquiring 100+ new Payroll customers.
- Wrote the ledger-based transaction management behind it, covering per diem and expense management, so an expense is compensated or deducted in the employee's monthly payroll.
- Synced user details between Payroll and Expense, with server jobs backfilling users and their expense history who existed before the integration, and batched per-organization imports with per-user opt-in.
- Built salary revision and payroll template customization used by 20K+ Payroll users, plus payroll runs and concurrent bank payment settlements.
- Built CSV and Excel import/export on Zoho's export-import framework: the file is processed in the back end, run through business logic, and applied to the database by scheduled import jobs.
- Secured the integration APIs: OWASP-based scanning, throttling on every API, JSON schema validation on every endpoint, and auth checks so no user can query another user's information.
- Led setup of the Continuous Integration system for the Zoho Books repository with GitLab CI/CD.
- Cut recurring production incidents ~30% by root-causing abnormalities and coordinating timely fixes across teams.
- Tuned query execution and concurrency for high-load Payroll operations with Java thread pools and async job processing, improving throughput and reducing contention.
- Built Vue.js interfaces for Zoho Finance workflows, wired to Java/Spring Boot REST endpoints.
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
- My role: the frontend, including the Cytoscape graph dashboard, the demo engine and the landing page, on a three-person team.
- Stack: Jac, FastAPI, MongoDB, Next.js + React, Python, TypeScript. Team repo: https://github.com/amirkhabaza/JacHacks2026

### NYC Real Estate Intelligence (May 2026): https://github.com/Badri-Rajendran/NYC-Real-Estate-Intelligence
An end-to-end ML pipeline that classifies NYC properties as undervalued, fair or overvalued using five public civic APIs, including Census, NYPD, NYC DOE and Walk Score. Includes an XGBoost feature-engineering pipeline, a hybrid recommender, and a Claude conversational agent for natural-language queries. Stack: Python, scikit-learn, XGBoost, SoQL, Claude.

### NYC Capital Budget Explorer: https://github.com/Badri-Rajendran/NYC_Capital_Budget_Explorer
A civic-transparency web platform that visualizes daily-updated city budget data and folds in user feedback, to foster accountability in government spending. Stack: JavaScript.

### This portfolio site and Badri.ai: https://github.com/Badri-Rajendran/Badri-Rajendran.github.io
The site you're reading this on, and me. The page is static and has no dependencies, no framework and no build step; it renders as an agent execution trace, where an SVG filament draws itself down the page as you scroll and each section lights up as a node, over a canvas starfield with a star-trail cursor. Badri.ai is the assistant docked beside it: answers stream in a word at a time from a small Python backend that keeps the model key server-side, answers only from a curated file of facts about me, refuses anything off-topic, and is rate-limited per visitor.
- Stack: vanilla HTML, CSS and JavaScript, SVG, Canvas 2D, Python, server-sent events.

## Skills
- Generative AI: Claude API, Gemini API, OpenAI API, LangChain, LangGraph, LangFuse (LLM tracing and observability), RAG, hybrid retrieval (BM25 + vector), cross-encoder reranking, multi-agent orchestration, MCP servers, embeddings and vector search, sentence-transformers, LLM-as-Judge evals, tool calling, prompt engineering, fine-tuning, Hugging Face.
- Languages: Java, Python, TypeScript, JavaScript, Kotlin, SQL, HTML, CSS.
- Frameworks: React, Redux, Vue, Angular, Next.js, Vite, Node.js, Express, Spring Boot, FastAPI, Flask, Django, TailwindCSS, JUnit, PyTest, Selenium.
- Mobile: Android, React Native, hybrid mobile apps, REST API integration.
- Data and ML: Pandas, NumPy, SciPy, scikit-learn, XGBoost, PyTorch, TensorFlow, Transformers, Matplotlib, Seaborn.
- Cloud: AWS (EC2, Lambda, S3, RDS, EKS, ECS, Fargate, API Gateway, CloudFormation, CloudWatch, SQS, SNS, IAM, VPC, Secrets Manager), Azure Container Apps, Cloudflare, serverless.
- Databases: PostgreSQL, MySQL, MongoDB, DynamoDB, Redis, pgvector, SQLAlchemy, Alembic.
- DevOps and tools: Docker, Kubernetes, Helm, Terraform, Jenkins, Ansible, GitHub Actions, GitLab CI/CD, Prometheus, Grafana, Linux, Bash.
- Architecture, practices and integrations: microservices, REST APIs, distributed systems, event-driven architecture, system design, test-driven development, Agile/Scrum, OAuth/JWT; payment and fintech APIs: Stripe (Billing, Identity), Plaid, Alpaca, Razorpay.

## Education
- M.S. in Computer Science, Stevens Institute of Technology, Hoboken, NJ, Aug 2024 – May 2026. Coursework: ML & Neural Networks, Data Mining, Distributed Systems, Software Architecture, Object-Oriented Design, Deep Learning, DevOps, Natural Language Processing, DBMS, Cloud Computing.
- B.E. in Computer Science, Anna University, Chennai, IN, Aug 2018 – May 2022.

## Profiles and contact
- Email: badriathindran@gmail.com
- Phone: +1 201-687-9279
- LinkedIn: https://www.linkedin.com/in/badri-rajendran/
- GitHub: https://github.com/Badri-Rajendran
- Résumé: https://badri-rajendran.github.io/BadriRajendran_Resume.pdf
- Portfolio: https://badri-rajendran.github.io
