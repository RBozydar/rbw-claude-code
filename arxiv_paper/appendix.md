# Pilot Study {#sec:app:pilot_study}

To evaluate the effectiveness of simple prompting as a method to configure an off-the-shelf language model to act as an orchestrator, we prompted GPT-5 and Qwen3-8B with a similar setting and the same prompt template we used in Section [\[sec:exp_settings\]](#sec:exp_settings){reference-type="ref" reference="sec:exp_settings"}, allowing them to use GPT-5, GPT-5-mini, Qwen3-32B, and Qwen2.5-Coder-32B as tools and instruct the orchestrator to achieve best results while maintaining lowest cost. We then ran the model on a set of 300 HLE problems with max_tokens=32,000 and temperature T=0 and monitored the average number of times each model referred to one of its model choices. The results are shown in Figure [\[fig:imbalanced-tool-calls\]](#fig:imbalanced-tool-calls){reference-type="ref" reference="fig:imbalanced-tool-calls"}. When Qwen3-8B serves as the orchestrator, it exhibits a strong tendency to delegate the task to GPT-5 (73% of the cases). We refer to this phenomenon as self-enhancement bias [@zheng2023judging], where the orchestrator favors its variants. In contrast, when GPT-5 serves as the orchestrator, it prefers to call GPT-5 or GPT-5-mini in 98% of the cases. We term this phenomenon other-enhancement bias, where the orchestrator favors stronger models regardless of cost considerations, even though humans instruct them to do so.

Such imbalanced invocation patterns highlight the limitations of using off-the-shelf language models as orchestrators by simple prompting: their decisions are heavily biased rather than balanced across available options, resulting in poor orchestration effectiveness. This observation motivates our method to train a dedicated small orchestrator to decide when and how to invoke more intelligent language models.

# Evaluation Benchmarks {#sec:app:evaluation_benchmarks}

-   **Humanity's Last Exam (HLE)** [@phan2025humanity]. A large-scale benchmark comprising PhD-level questions across mathematics, humanities, natural sciences and more. It evaluates the model capabilities to perform iterative search and intensive reasoning. Questions are multiple-choice or short-answer, with 10--14% requiring images. We use the text-only subset, designed to be unambiguous and not solvable by simple web search.

-   **FRAMES** [@krishna2024factfetchreasonunified]. A dataset for end-to-end evaluation of retrieval-augmented generation (RAG), covering factuality, retrieval accuracy, and reasoning. It contains 824 multi-hop questions requiring 2--15 Wikipedia articles, spanning numerical, tabular, temporal, and multi-constraint reasoning.

-   **$\tau^2$-Bench** [@barres2025tau]. A benchmark to evaluate model capabilities to use tools and solve problems in conversations with users. It includes tasks in three domains: telecom, retail and airline.

# Model description for Qwen3-32B {#sec:app:model_description}

The model shows advanced mathematical and quantitative reasoning, often solving complex problems and only faltering on highly specialized or computationally heavy items. Scientific domain knowledge is strong---especially in biology---with solid performance in physics and engineering; chemistry is mixed, with notable weaknesses in exact nomenclature and InChI outputs. Logical problem-solving is high, while humanities knowledge is moderate and uneven, with gaps in niche scholarly details. Coding and function call abilities are moderate, where it makes mistakes in parameters from time to time. Overall, the model has broad knowledge and robust analytic skills, but accuracy drops on narrow, recent, or rote-precision tasks, particularly in chemical informatics.

# Tools in training {#sec:app:tool_train}

Below is the complete list of tools used in the training. For each example rollout, we randomly sample a subset of them to simulate heterogeneous availability of tools:

-   Query writer: GPT-5 [@gpt-5], GPT-5-mini [@gpt-5], meta-llama/Llama-3.3-70B-Instruct [@dubey2024llama], meta-llama/Llama-3.1-8B-Instruct [@dubey2024llama], deepseek-ai/DeepSeek-R1 [@guo2025deepseek], nvidia/Llama-3_1-Nemotron-Ultra-253B-v1 [@bercovich2025llama], microsoft/Phi-4-mini-instruct [@abouelenin2025phi], google/gemma-3-27b-it [@team2025gemma], Qwen/Qwen3-32B [@yang2025qwen3]

-   Web search: We use Tavily search API [^1] to provide orchestrator real-time web access.

-   Local search: Faiss index with Qwen/Qwen3-Embedding-8B [@zhang2025qwen3]

-   Code writer + interpreter: We use GPT-5 [@gpt-5], GPT-5-mini [@gpt-5], bigcode/starcoder2-15b [@lozhkov2024starcoder], and Qwen/Qwen2.5-Coder-32B-Instruct [@hui2024qwen2] as code expert models to write code. We also implemented a Python sandbox to execute the code.

-   Math models: Qwen/Qwen2.5-Math-72B [@yang2024qwen2], Qwen/Qwen2.5-Math-7B [@yang2024qwen2]

-   Generalist models: GPT-5 [@gpt-5], GPT-5-mini [@gpt-5], meta-llama/Llama-3.3-70B-Instruct [@dubey2024llama], meta-llama/Llama-3.1-8B-Instruct [@dubey2024llama], deepseek-ai/DeepSeek-R1 [@guo2025deepseek], nvidia/Llama-3_1-Nemotron-Ultra-253B-v1 [@bercovich2025llama], microsoft/Phi-4-mini-instruct [@abouelenin2025phi], Qwen/Qwen3-32B [@yang2025qwen3]

# Third-party API {#sec:app:api_pricing}

Here is a list of third-party APIs. We used pricing configurations for training:

-   TogetherAI: https://www.together.ai/

-   Venice AI: https://docs.venice.ai/overview/about-venice

-   Chutes: https://chutes.ai/

-   NEBIUS: https://nebius.com/

-   Lambda: https://lambda.ai/

-   Hyperbolic: https://docs.hyperbolic.xyz/docs/welcome-to-hyperbolic

-   Cloudflare: https://developers.cloudflare.com/

-   Novita: https://novita.ai/

-   AIML: https://aimlapi.com/

-   Fireworks AI: https://fireworks.ai/

In the evaluation, we apply the pricing from Together AI for fair comparison.

# Humane preference example {#sec:app:preference_example}

**Tools**; $T$ = $[$ Web search, local search, Qwen/Qwen3-235B-A22B, meta-llama/Llama-3.3-70B-Instruct, o3-mini, o3 $]$\
Preference instruction: $PI$ = I am a company employee and there is some confidential information in my server. There are many GPUs in the server, so I can host open-sourced models or retrievers. It would be great if we can avoid API calling as much as possible.\
Preference vector: $P$ = \[0,1,1,1,0,0,0,0,0\] Explanation: The first digit in the preference vector corresponds to the first tool in $T$; The second digit in the preference vector corresponds to the second tool in $T$, etc. The last three digits in $P$ corresponds to accuracy, cost and latency, aligned with the definitions in §[\[sec:end2endRL\]](#sec:end2endRL){reference-type="ref" reference="sec:end2endRL"}. Therefore, this preference vector means the user prefers to use local search, Qwen/Qwen3-235B-A22B, meta-llama/Llama-3.3-70B-Instruct.

# Use of LLMs Disclosure

We used GPT-5 to polish the writing, primarily in the Abstract, Introduction, Methodology, and Experiments sections, to improve the grammar, clarity, and readability. The research ideas, methodology, experiments, and analyses were entirely conducted by the authors.

# Generalization of pricing configurations {#sec:app:generalization_pricing}

In Section [\[sec:main:generalization\]](#sec:main:generalization){reference-type="ref" reference="sec:main:generalization"}, we examined Orchestrator-8B's ability to generalize to unseen tools. Here, we investigate its generalization across heterogeneous pricing regimes, where the same tools are assigned different costs. We evaluate whether the model adapts by adjusting its tool-calling strategy to optimize outcomes, efficiency, and alignment with user preferences---reflecting realistic settings in which tool costs vary across users. We test Orchestrator-8B under a pricing configuration not encountered during training. Specifically, we use the pricing configuration from deepinfra[^2]. As shown in Table [\[tab:generalization_pricing_config\]](#tab:generalization_pricing_config){reference-type="ref" reference="tab:generalization_pricing_config"}, it consistently delivers superior performance, cost efficiency, and accuracy. These results demonstrate that training with diverse pricing configurations produces a model that is not constrained to a particular tool setup and can robustly generalize across diverse user scenarios.

# Data Synthesis {#sec:app:data_synthesis}

#### .

To enable end-to-end RL training of Orchestrator, we require data involving user-agent-tool interaction trajectories, but such verifiable data is scarce. To generate such high-quality data, we devise a two-step process: (1) simulating rich user-agent-tool environments, including creating database schemas and tool APIs; and (2) based on the environment, generating diverse user tasks together with their corresponding ground truth solutions. We further ensure quality by carefully verifying that each task is solvable using the provided databases and tool APIs. Figure [\[fig:data_synthesis\]](#fig:data_synthesis){reference-type="ref" reference="fig:data_synthesis"} provided an overview of this process. Firstly, to simulate real-world user-agent-tool environments scalably, we choose a domain $D$ and then ask an LLM to generate a database which includes schema, major subjects to focus on and database entries (as illustrated in the top-left of Figure [\[fig:data_synthesis\]](#fig:data_synthesis){reference-type="ref" reference="fig:data_synthesis"}). Each entry is then checked to ensure coherence, adherence to the schema, and consistency across content, logic, and entities. Based on the given domain $D$, LLM proposes frequently-used tools. Secondly, to increase the diversity of the task instructions, LLM first proposes diverse intents frequently seen in domain $D$, which are later converted to specific tasks based on detailed database information. Each generated task consists of task instruction $I$, gold function calls $A={a_1, a_2, ..., a_l}$, and short information $o$ that must be mentioned during the process to solve the task. To enhance the difficulty of the generated tasks, we leverage an additional LLM to complicate tasks by adding more complexities such as more constraints.

To ensure the quality of the synthesized data, we filter the data to remove a task if: (1) the execution of golden function calls reports an error; (2) LLMs cannot solve it in pass@$8$; and (3) the task can be solved without any actions. In Appendix [10](#sec:app:details_of_toolscale){reference-type="ref" reference="sec:app:details_of_toolscale"}, we list the statistics of the generated data in each domain. More examples and prompts used to synthesize data can be found in Appendix [11](#sec:app:data_synthesis_prompts){reference-type="ref" reference="sec:app:data_synthesis_prompts"}. To evaluate whether a trajectory $\tau$ solves the given task, we define the following criteria: (1) *execution correctness*, namely whether the database content matches after executing the golden function calls $A$ and the trajectory $\tau$; (2) *process fidelity*, i.e., whether the predefined information $o$, which is required to be communicated in the process to solve the task, is mentioned in $\tau$; (3) *operation completeness*, that is whether the database entries operated in the ground truth trajectory $A$ are also operated in $\tau$. We consider $\tau$ solves the task if all of three criteria are satisfied, or fails otherwise.

::: table*
                         **HLE ($\uparrow$)**   **Frames ($\uparrow$)**   **$\tau^2$-Bench ($\uparrow$)**   **Cost ($\downarrow$)**   **Latency ($\downarrow$)**
  --------------------- ---------------------- ------------------------- --------------------------------- ------------------------- ----------------------------
        Qwen3-8B                 29.7                    68.2                          71.9                          27.4                        17.9
      Nemotron-49B               25.6                    57.8                          66.3                          24.3                        17.2
      Llama-3.3-70B              19.6                    52.2                          55.4                          17.9                        12.0
     Qwen3-235B-A22B             32.4                    74.1                          75.3                          27.9                        20.8
     Claude Opus 4.1             34.5                    72.3                          76.4                          52.3                        25.1
          GPT-5                  20.8                    57.3                          61.9                          17.5                        13.2
   **Orchestrator-8B**         **36.9**                **76.6**                      **80.4**                       **7.5**                    **7.8**
:::

# Breakdown of  {#sec:app:details_of_toolscale}

::: table*
:::

# Data synthesis prompts and examples {#sec:app:data_synthesis_prompts}

::: {#tab:prompt_generate_subject}
  ------------------------------------------------
  Generate a list of major subjects in {domain}.
  Output using the following format:
  $[$subject1, subject2, \...$]$
  ------------------------------------------------

  : Model prompts to generate subjects in a domain
:::

[]{#tab:prompt_generate_subject label="tab:prompt_generate_subject"}

::: {#tab:prompt_generate_schema}
  ----------------------------------------------------------
  {demo_schema}
  Generate another schema of similar formats for {domain}.
  ----------------------------------------------------------

  : Model prompts to generate schema in a domain
:::

[]{#tab:prompt_generate_schema label="tab:prompt_generate_schema"}

::: {#tab:prompt_generate_db_entry}
  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Schema
  {schema}
  Following the schema, write records in the subject {subject}. Make sure that the values align with the definitions in the schema and are consistent in different places. Use the following format to output:
  { "\...\": \..., "\...\": \..., }
  Wrap the dictionary within .
  --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

  : Model prompts to generate database entry
:::

[]{#tab:prompt_generate_db_entry label="tab:prompt_generate_db_entry"}

::: {#tab:prompt_validate_db_entry}
  --------------------------------------------------------------------------------------------------------------------------------------------
  Schema
  {schema}
  Database entry
  {db_entry}
  Please check whether the following conditions are satisfied:
  Condition 1. The database entry strictly aligns with the fields and type definitions in the schema.
  Condition 2. The values in the database entry are consistent across different places, e.g., id, name, etc.
  Condition 3. The database content is logical, natural, and reasonable.
  Output using the following format:
  { "condition 1\": "satisfied or not satisfied, "condition 2\": "satisfied or not satisfied, "condition 3\": "satisfied or not satisfied, }
  --------------------------------------------------------------------------------------------------------------------------------------------

  : Model prompts to validate database entry
:::

[]{#tab:prompt_validate_db_entry label="tab:prompt_validate_db_entry"}

::: {#tab:prompt_generate_functions}
  ---------------------------------------------------------------------------------------------------------------------------
  Demonstration function
  {demo_function}
  Following the formats of demonstration function, write frequently-used functions in {domain}. Wrap the functions within .
  ---------------------------------------------------------------------------------------------------------------------------

  : Model prompts to generate functions
:::

[]{#tab:prompt_generate_functions label="tab:prompt_generate_functions"}

::: {#tab:prompt_generate_intents}
  ------------------------------------------------------------------------------------------------------------------------
  Functions
  {functions}
  Propose realistic intents in {domain} that could be solved by the functions above. Use the following format to output:
  .
  $[$
  "purpose 1\",
  "purpose 2\",
  \...
  $]$
  .
  ------------------------------------------------------------------------------------------------------------------------

  : Model prompts to generate intents
:::

[]{#tab:prompt_generate_intents label="tab:prompt_generate_intents"}

::: {#tab:prompt_generate_tasks}
  -----------------------------------------------------------------------------------------
  Functions
  {functions}
  Database
  {database}
  Propose a realistic task with the intent: {intent}. Use the following format to output:
  .
  {task_template}
  .
  -----------------------------------------------------------------------------------------

  : Model prompts to generate tasks
:::

[]{#tab:prompt_generate_tasks label="tab:prompt_generate_tasks"}

::: {#tab:prompt_evolve_tasks}
  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Functions
  {functions}
  Database
  {database}
  Old task: {task}
  Make a new task by adding more complexity to the old task. You can add constraints, involve more entities, make the situation more tricky, etc. Use the following format to output:
  .
  {task_template}
  .
  -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

  : Model prompts to evolve tasks
:::

[]{#tab:prompt_evolve_tasks label="tab:prompt_evolve_tasks"}

::: {#tab:schema_example}
  ------------------------------------------------------------------------------------------------------------------------------------------------
  {
  "movies\": {
  "MMMMMMM\": { movie_id
  "movie_id\": \"MMMMMMM\",
  "title\": \"\...\",
  "genres\": $[$"Action\", "Adventure\", "Comedy\", "Drama\", "Horror\", "Thriller\", "Romance\", "Science Fiction\", "Fantasy\", "Mystery\"$]$,
  "runtime_minutes\": \...,
  "mpaa_rating\": "\...\",
  "languages_audio\": $[$\"\...\"$]$,
  "subtitles\": $[$\"\...\"$]$,
  "formats\": $[$\"2D\", \"3D\", \"IMAX\", \"Dolby\"$]$,
  "release_date\": "YY-MM-DD\",
  "end_of_run_est\": "YY-MM-DD\",
  "cast\": $[$
  { "name\": "\...\", "role\": "\...\" }
  $]$,
  "crew\": {
  "director\": "\...\",
  "writer\": "\...\",
  "producer\": "\...\",
  "music\": "\...\"
  },
  \"synopsis\": \"\...\"
  },
  \...
  },
  \...
  }
  ------------------------------------------------------------------------------------------------------------------------------------------------

  : Database schema example
:::

[]{#tab:schema_example label="tab:schema_example"}

# Calculation of rewards for preference-aware benchmark {#sec:app:preference_reward_test}

During training, we directly follow the Equation [\[eq:final_reward\]](#eq:final_reward){reference-type="ref" reference="eq:final_reward"} to calculate rewards. In the evaluation, we use the following procedure. Following the definition in §[\[sec:end2endRL\]](#sec:end2endRL){reference-type="ref" reference="sec:end2endRL"}, we have a tool set $\left\{t_1, t_2, ..., t_n\right\}$ and a rollout trajectory $\tau$, we consider the vector $M^{\tau}=[m^{\tau}_{t_1}, m^{\tau}_{t_2}, \ldots, m^{\tau}_{t_n},r^{\tau}_\text{outcome},r^{\tau}_\text{compute},r^{\tau}_\text{latency}]$, where $m^{\tau}_{t_\bullet}$ is the number of times tool $t_\bullet$ is invoked in $\tau$. In the evaluation, we obtain the baseline vector $M_0$ by running the starting checkpoint, e.g., Qwen3-8B. For example, if we would like to evaluate a checkpoint $\mathit{CKPT}_s$ that is trained for $s$ steps from a base Qwen3-8B model, then we first run Qwen3-8B on the benchmark and record the vector $M^{\tau(e)}_0$ as the baseline vector for the Qwen3-8B's trajectory $\tau(e)$ for each example $e$ of the benchmark. We then obtain $M^{\tau(e)}_s$ by running $\mathit{CKPT}_s$ on the same example $e$. $M^{\tau(e)}_s$ is normalized as $$M^{{\tau(e)}}_{\text{normalized}, s}[k] = 
\begin{cases}
M^{\tau(e)}_s[k]/max(1,M^{\tau(e)}_0[k]) & \text{if } 1 \leq k \leq n+1 \\
M^{\tau(e)}_0[k]/max(1,M^{\tau(e)}_s[k]) & \text{otherwise}.
\end{cases}
\label{eq:normalize_reward_eval}$$ We then proceed to calculate the final preference-aware reward for the example $e$ as: $$\small
R^e(\tau) = 
\begin{cases}
M^{{\tau(e)}}_{\text{normalized}, s}\cdot P & \text{if } r_{\text{outcome}(\tau)} \\
0 & \text{otherwise}.
\end{cases}
\label{eq:final_reward_eval}$$

The benchmark result is calculated as the sum of $R^e(\tau)$ over the examples $e$ of the benchmark.

::: table*
:::

::: table*
::: tabular
@ c p2.7cm c c c @ **Tools** & **Model(s)** & **$\tau^2$-Bench ($\uparrow$)** & **Cost ($\downarrow$)** & **Latency ($\downarrow$)**\
& Qwen3-8B & 40.7 & 1.6 & 2.3\
& Llama-Nemotron-49B & 23.2 & 2.7 & 3.6\
& Llama-3.3-70B & 17.6 & 3.1 & 4.5\
& Qwen3-235B-A22B & 52.9 & 12.6 & 10.6\
& Claude Opus 4.1 & 46.0 & 81.2 & 32.8\
& GPT-5 & 77.7 & 31.3 & 20.2\
& Qwen3-8B & 72.3 & 27.9 & 18.4\
& Llama-Nemotron-49B & 66.7 & 25.8 & 17.5\
& Llama-3.3-70B & 55.8 & 20.1 & 14.2\
& Qwen3-235B-A22B & 75.6 & 30.0 & 22.6\
& Claude Opus 4.1 & 76.8 & 52.8 & 24.1\
& GPT-5 & 62.3 & 18.2 & 14.5\
&**Orchestrator-8B** & **80.2** & **10.3** & **8.6**\
:::
:::

[^1]: <https://www.tavily.com/>

[^2]: https://deepinfra.com
