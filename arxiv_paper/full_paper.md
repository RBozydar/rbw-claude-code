::: figure*
![image](figs/figure_final_results.pdf){width="\\linewidth"}

![image](figs/cost_performance.pdf){width="\\linewidth"}
:::

# Introduction

Large language models (LLMs) have been reported to have made remarkable strides towards superhuman intelligence but remain of limited utility in complex agentic tasks such as those posed by the Humanity's Last Exam (HLE) [@phan2025humanity]. Tool use is a promising avenue for the extension of their capabilities beyond what can be learned from the training data. By calling on external resources through search engines and code interpreters, tool use has been shown to enhance accuracy and reduce hallucinations [@qintoolllm; @schick2023toolformer; @qin2024tool; @gehring2024rlef; @qian2024tell; @yu2024steptool; @goldie2025synthetic; @zhang2025nemotron; @qian2025toolrl].

Prior research on tool-use agents has primarily focused on equipping a single powerful model with utility tools such as web search or calculators. While effective in many scenarios, this approach underutilizes the potential of tools: humans, when reasoning, routinely extend themselves by calling upon resources of greater-than-human intelligence, from domain experts to sophisticated processes and software systems. Motivated by this observation, we propose the *orchestration paradigm*. Under this paradigm, intelligence emerges not from a monolith but from a composite system. At the center of the system lies an *orchestrator* model, whose responsibility is to invoke the right tools for the given task, and to do so in the right order to accomplish the task. The crucial difference to the standard monolithic setup featuring a single powerful model is that in addition to deterministic utilities such as web search functions and code interpreters, models of various capabilities are made available to the orchestrator as *intelligent tools*. The use of tools of different levels of intelligence comes at varying costs, and the challenge for the orchestrator is then to dynamically decide on which tools to invoke in order to solve the task while respecting user preferences for various tools and minimizing the cost. By delegating narrowed-down sub-problems of a larger effort requiring intelligence to intelligent tools instead of handling the entire effort by a single generalist, orchestration teems with the promise of exhibiting higher intelligence than any of the system's tools and leading monolithic solutions alike.

One approach to implementing the orchestrator paradigm is to employ a language model as the orchestrator and allow it to invoke stronger models only when it deems it necessary. This can be done naively by *prompting* an off-the-shelf language model or by *training* a general-purpose orchestrator. For the former, we find that relying on straightforward model prompting is brittle and introduces systemic biases. As shown in Figure [\[fig:imbalanced-tool-calls\]](#fig:imbalanced-tool-calls){reference-type="ref" reference="fig:imbalanced-tool-calls"} (left and middle), GPT-5 disproportionately delegates tasks to GPT-5-mini, while Qwen3-8B defers to GPT-5 at a markedly higher rate. This illustrates two present issues of prompting in the context of complex tool orchestration: (i) the overuse of developmentally-related variants of oneself, i.e., *self-enhancement bias* [@zheng2023judging], and (ii) defaulting to the strongest available tool regardless of the cost or relative utility (see Appendix [9](#sec:app:pilot_study){reference-type="ref" reference="sec:app:pilot_study"} for more details and §[4](#sec:exp_settings){reference-type="ref" reference="sec:exp_settings"} for a thorough comparison to baselines). As such, we conclude that the scenarios in which an orchestrating model may call on models and tools of capabilities both inferior and superior to its own are idiosyncratic in the context of model tool calling and warrant their own approach to training. In addition, controllability in tool-use agents remains underexplored along two axes: cost--efficiency and user preferences (cf. §[7](#sec:related_work){reference-type="ref" reference="sec:related_work"}).

![Overview of Orchestrator. Given a task, Orchestrator alternates between reasoning and tool calling in multiple turns to solve it. Orchestrator interacts with a diverse tool set, including basic tools (web search, functions such as `get_flight_status`, etc.), specialized LLMs (coding models, math models, etc.) and generalist LLMs (GPT-5, Claude Opus 4.1, etc.). In training under ToolOrchestra, Orchestrator is jointly optimized by outcome, efficiency and preference rewards via reinforcement learning.](figs/fig1.pdf){#fig:fig1 width="\\linewidth"}

::: wrapfigure
r0.4 ![image](figs/figure_imbalanced_tool_calling_preferences_2.pdf){width="0.41\\columnwidth"}
:::

We address these shortcomings by proposing ToolOrchestra (shown in Figure [1](#fig:fig1){reference-type="ref" reference="fig:fig1"}), a novel method for training a small language model to act as the orchestrator -- the "brain" of a heterogeneous tool-use agent. Using ToolOrchestra, we produce the Orchestrator, an 8B-parameter model trained end-to-end with reinforcement learning (RL) to decide when and how to invoke more intelligent language models and various tools such as web search or code interpreters, and how to combine them in multi-turn reasoning. Our reward design balances three objectives -- correctness of the final outcome, efficiency in resource usage, and alignment with user preferences -- to yield a cost-effective and user-controllable tool-use policy. To aid RL training, we build an automatic data synthesis pipeline that generates thousands of verifiable multi-turn tool-use training examples with complex environments across 10 domains. We will make the resulting dataset, ToolScale, publicly available to facilitate further research on tool-use agent training.

In our experiments, we rigorously evaluate the merits of our approach on three challenging tasks. On HLE [@phan2025humanity], a benchmark consisting of difficult questions across many disciplines, we find that Orchestrator substantially outperforms prior methods with far lower computational cost. We also test on $\tau^2$-Bench [@barres2025tau], a function-calling benchmark, where Orchestrator demonstrates the ability to schedule a variety of tools effectively, calling a large model (GPT-5) in only $\sim$`<!-- -->`{=html}40% of the steps and utilizing cheaper models or tools for the rest, yet still exceeding the performance of an agent that uses the large model for every step. Finally, additional evaluations on the FRAMES [@krishna2024factfetchreasonunified], a factuality reasoning benchmark, provide further evidence of the versatility and robustness of our approach. We observe that even though the training and testing tasks differ markedly, the RL-trained Orchestrator adapts its tool-use policy to new challenges, indicating a high degree of general reasoning ability.

Our contributions can be summarized as follows: (1) We introduce ToolOrchestra, a method for training a small language model to serve as the orchestrator of a diverse toolkit, including classical tools and more intelligent models. This dovetails with recent developments in the field testifying that small language models are often sufficiently powerful and far more economical in agentic systems [@belcak2025small; @zhao2025llm]. (2) We develop a novel reward training design that goes beyond accuracy. The resulting Orchestrator is trained end-to-end to balance task outcome correctness, efficiency in cost and latency, and alignment with user cost and tool preferences. (3) We demonstrate that Orchestrator trained by ToolOrchestra achieves state-of-the-art performance on challenging reasoning benchmarks, surpassing frontier models while using only a fraction of their compute and wall-clock time, and that it generalizes robustly to unseen tasks and tools.

# Agentic Problem Formulation {#sec:problem_formulation}

## Task Formulation

We investigate multi-turn tool-use agentic tasks and formalize them as a Markov Decision Process (MDP) $\mathcal{M}=(\mathcal{U},\mathcal{S},\mathcal{A},\mathcal{O},\mathcal{T},\mathcal{Z},r,\rho,\gamma)$ following conventions similar to prior work [@xi2024agentgym; @zhou2024archer; @xi2025agentgym]. We are given an instruction $u\in\mathcal{U}$, user action preferences $p = \left(0 \leq p_{a} \leq 1 \text{ for } a \in \mathcal{A}\right)$, an initial state drawn from $\rho(\cdot\,|\,u)$, an initial observation $o_0\in\mathcal{O}$, and the environment state space $\mathcal{S}$. At step $k$, the Orchestrator chooses an action $a_k\in\mathcal{A}$ according to a policy $\pi_\theta(a_k\,|\,h_k)$ where $h_k=(u,o_0,a_0,o_1,\dots,a_{k-1},o_k)$ is the interaction history. The environment transitions according to $\mathcal{T}(s_{k+1}\,|\,s_k,a_k)$ and emits an observation $o_{k+1}\sim\mathcal{Z}(\cdot\,|\,s_{k+1},a_k)$. The actions $a_i$ come at costs $c_i$ and operational latency $l_i$, and the alignment of each action with user preferences is $p_{a_i}$. After $N$ interaction steps, Orchestrator has traced the trajectory $\tau=h_{N}$ and the environment provides a reward $r(\tau) \in [0,1]$ based on its correctness. Our goal is to maximize the correctness reward $r(\tau)$ and the overall user preference alignment $\sum p_{a_i}$ while minimizing the total cost $\sum c_i$ and the aggregate latency $\sum l_i$.

## Multi-Turn Rollout

Given a user task, Orchestrator produces a solution via an iterative rollout that interleaves tool use with environment feedback to form a trajectory of turns. The rollout is initialized with a predefined system prompt and the question; the model (assistant role) then generates an initial step that ends with an EOS token. Each turn follows a *reasoning--action--observation* loop: (1) **Chain-of-thought (reasoning).** The Orchestrator analyzes the current state and plans the next action. (2) **Tool call (action).** Based on its reasoning, Orchestrator selects a tool from the available set (e.g., APIs, specialized models, code interpreters) and specifies parameters. (3) **Tool response (observation).** If a tool call is present, the tool-call block is extracted and executed by the environment; the resulting output is appended to the context under the user role and fed back to the model for the next turn. This process repeats until Orchestrator receives a termination signal from the environment or the rollout reaches a maximum of 50 turns.

# ToolOrchestra {#sec:main_method}

Our approach, ToolOrchestra, centers on training a small language model as an intelligent agentic model capable of solving complex tasks by dynamically selecting and utilizing a wide variety of external tools. We hypothesize that small language models suffice for this purpose if they are taught to coordinate more intelligent tools strategically, and thus choose to train an 8B model. ToolOrchestra consists of an end-to-end reinforcement learning setup where the model under training, termed Orchestrator, learns to generate optimal multi-step reasoning and tool-use trajectories. The overall architecture is illustrated in Figure [1](#fig:fig1){reference-type="ref" reference="fig:fig1"}.

## Unified Tool Calling {#sec:unified_tool_call}

In contrast to prior tool-use agents [@li2025torl; @jin2025search], we broaden the toolset to include domain-specialized models and expose all tools through a single, unified interface. Tools are specified in JSON as a list of objects; each object defines the tool name, description, and a typed parameter schema (names and descriptions). When LLMs are used as tools, we obtain their descriptions with the following steps: (1). randomly sample 10 training tasks; (2). obtain the trajectories of LLMs to finish these tasks; (3). Ask another LLM to write the description based on the task instructions, LLM trajectories and whether LLMs complete the tasks. In Appendix [11](#sec:app:model_description){reference-type="ref" reference="sec:app:model_description"}, we show an example description of Qwen3-32B. The complete catalog of tools used in our training is provided in Appendix [12](#sec:app:tool_train){reference-type="ref" reference="sec:app:tool_train"}.

## End-to-End Agentic Reinforcement Learning {#sec:end2endRL}

#### Reward design.

We introduce outcome, efficiency and preference rewards into the training. For outcome reward, each rollout trajectory $\tau$ in a rollout batch $\mathrm{T}$ receives a binary accuracy reward $r_{\text{outcome}}(\tau) \in \{0,1\}$ based on whether $\tau$ solves the task: $$\small
r_{\text{outcome}}(\tau) = 
\begin{cases}
1 & \text{if } \text{solved}(\tau), \\
0 & \text{otherwise}.
\end{cases}
%\label{eq:outcome_reward}$$

We leverage GPT-5 as a judge to compare the answers, e.g., a name, a date, etc., providing greater flexibility in handling diverse predictions.

To encourage efficient solutions, we penalize the model under training for excessive compute or latency with the following rewards: $r_\text{compute}(\tau) = -\$(\tau)$, $r_\text{latency}(\tau) = -\mathit{Clock}(\tau)$, where $\$(\tau)$ is the monetary cost of $\tau$ and $\mathit{Clock}(\tau)$ is the consumed wall-clock time by $\tau$. To establish a unified measurement on the compute of both open-sourced and proprietary models, we convert both the input tokens and output tokens to monetary costs following the third-party API pricing systems. See more details in Appendix [13](#sec:app:api_pricing){reference-type="ref" reference="sec:app:api_pricing"}.

Preference reward is designed to encourage models to consider user preferences when choosing tools at each step. Given a set of tools $\left\{t_1, t_2, ..., t_n\right\}$ and a rollout trajectory $\tau$, we consider the vector $M^{\tau}=[m^{\tau}_{t_1}, m^{\tau}_{t_2}, \ldots, m^{\tau}_{t_n},r_\text{outcome}(\tau),r_\text{compute}(\tau),r_\text{latency}(\tau)]$, where $m^{\tau}_{t_\bullet}$ is the number of times tool $t_\bullet$ is invoked in $\tau$, $M^{\tau}[n+1]=r_\text{outcome}(\tau)$.

During RL training, we normalize each element $M^{\tau}[k]$ for $1 \leq k \leq n+3$ over the rollout batch $\mathrm{T}$ as follows: $M^{\tau}_\text{normalized}[k] = (M^{\tau}[k]-M^{\mathrm{T}}_{\text{min}}[k])/(M^\mathrm{T}_{\text{max}}[k]-M^\mathrm{T}_{\text{min}}[k])$, where $M^\mathrm{T}_{\text{min}}[k]$ and $M^\mathrm{T}_{\text{max}}[k]$ are minimum and maximum value for $M^{\bullet}[k]$ in the batch $\mathrm{T}$. If $M^\mathrm{T}_{\text{max}}[k]=M^\mathrm{T}_{\text{min}}[k]$, we disregard $M^{\tau}[k]$ by setting it to zero. We calculate the final reward for a trajectory $\tau$ as: $$\small
R(\tau) = 
\begin{cases}
M_{\text{normalized}}^{\tau} \cdot P & \text{if } r_{\text{outcome}}(\tau) \\
0 & \text{otherwise}.
\end{cases}
\label{eq:final_reward}$$

where $P=\left[p_{t_1},p_{t_2}, ..., p_{t_n}, p_\text{outcome}, p_\text{compute}, p_\text{latency}\right]$ ($0 \leq p_{\bullet} \leq 1$) is the preference vector, indicating the extent the user would like to optimize $M[{\bullet}]$. For example, $P[1] = p_{t_1}=1$ indicates strong user preference to use the tool $t_1$, while $P[n+1] = p_\text{outcome} = 1$ and $P[n+2] = p_\text{compute}=0$ implies that the user wants to exclusively optimize accuracy without considering the computational cost.

#### Training procedure.

Orchestrator is fine-tuned using a policy gradient reinforcement learning algorithm, specifically Group Relative Policy Optimization (GRPO) [@shao2024deepseekmath]. For each task in a batch, the policy $\pi_\theta$ generates a batch of trajectories ${\mathrm{T}}$. Each trajectory $\tau \in \mathrm{T}$ is assigned a scalar reward $R(\tau)$ (as calculated in Equation [\[eq:final_reward\]](#eq:final_reward){reference-type="ref" reference="eq:final_reward"}), and GRPO normalizes this reward within its group to compute an advantage: $$\small
A(\tau) = \frac{R(\tau) - \text{mean}_{\tau \in \mathrm{T}}{R(\tau)}}{\text{std}_{\tau \in \mathrm{T}}{R(\tau)}}.$$ The policy is then updated to maximize the clipped surrogate objective: $$\small
\mathcal{L}_{\text{GRPO}}(\theta) = \mathbb{E}{\tau \sim \pi_\theta} \Bigg[
\min\Big(
\text{ratio}_\theta(\tau) A(\tau), 
\text{clip}(\text{ratio}_\theta(\tau), 1 - \epsilon, 1 + \epsilon) A(\tau)
\Big)
\Bigg],$$ where $\text{ratio}_\theta(\tau) = \frac{\pi_\theta(\tau)}{\pi_{\text{old}}(\tau)}$ is the likelihood ratio between the current and previous policy.

#### Training techniques.

To stabilize RL training and avoid KL loss explosion for this agent system, we perform the following during backward propagation: (1) *homogeneity filtering*, when the standard deviation of rewards in a rollout batch is smaller than $0.1$, because this indicates that most rollouts in a batch exhibit similar behaviors, and provides weak training signals; (2) *format consistency filtering*, when the example output is not aligned with the tool call format; (3) *invalid output filtering*, when the example does not produce a valid answer or output.

![Overview of ToolScale data synthesis pipeline. Starting from a domain, LLM will (1) firstly generate domain-specific database and tool APIs to simulate the environment and (2) then generate diverse user tasks together with their corresponding golden actions.](figs/fig_algo1.pdf){#fig:data_synthesis width="0.95\\linewidth"}

## Data Synthesis {#subsec:data_synthesis}

#### ToolScale.

To enable end-to-end RL training of Orchestrator, we require agentic tool-call tasks, but verifiable data of this kind is scarce. To generate such data, we devise a two-step process: (1) simulating rich user-agent-tool environments, including creating database schemas and tool APIs; and (2) generating diverse user tasks together with their corresponding ground truth solutions based on the environment. Figure [2](#fig:data_synthesis){reference-type="ref" reference="fig:data_synthesis"} provided an overview of this process. Firstly, to simulate real-world user-agent-tool environments scalably, we choose a domain $D$ and then ask an LLM to generate a database which includes schema, major subjects to focus on and database entries (as illustrated in the top-left of Figure [2](#fig:data_synthesis){reference-type="ref" reference="fig:data_synthesis"}). Based on the given domain $D$, LLM proposes frequently-used tools. Secondly, to increase the diversity of the task instructions, LLM first proposes diverse intents frequently seen in domain $D$, and then convert them to specific tasks based on detailed database information. Each generated task consists of task instruction $I$, golden function calls $A={a_1, a_2, ..., a_l}$, and short information $o$ that must be mentioned during the process to solve the task. To enhance the difficulty of the generated tasks, we leverage an additional LLM to complicate tasks by adding more complexities such as more constraints. To ensure the quality of the synthesized data, we filter the data to remove a task if: (1) the execution of golden function calls reports an error; (2) LLMs cannot solve it in pass@$8$; and (3) the task can be solved without any actions. In Table [\[tab:data_statistics\]](#tab:data_statistics){reference-type="ref" reference="tab:data_statistics"}, we list the statistics of the generated data in each domain. More examples and prompts used to synthesize data can be found in Appendix [17](#sec:app:data_synthesis){reference-type="ref" reference="sec:app:data_synthesis"}. To evaluate whether a trajectory $\tau$ solves the given task, we define the following criteria: (1) *execution correctness*, namely whether the database content matches after executing the golden function calls $A$ and the trajectory $\tau$; (2) *process fidelity*, i.e., whether the predefined information $o$, which is required to be communicated in the process to solve the task, is mentioned in $\tau$; (3) *operation completeness*, that is whether the database entries operated in the ground truth trajectory $A$ are also operated in $\tau$. We consider $\tau$ to solve the task if each of these three criteria is satisfied, and fail to solve it otherwise.

#### User preference.

Different users possess different preferences. For example, some users prefer local search to safeguard privacy, while others opt for internet-based search to access broader knowledge. To train Orchestrator to account for such preferences in tool selection, we construct pairs of preference instruction $PI$ and preference vectors $P$, which indicate the extent a user would like to optimize certain features, e.g., latency, or the frequency to use a particular tool (§[3.3](#subsec:data_synthesis){reference-type="ref" reference="subsec:data_synthesis"}). Given a tool set $\left\{t_1, t_2, ..., t_n\right\}$, and the corresponding configuration metadata (e.g., tool price, latency), an LLM proposes diverse pairs of $\left(PI,P\right)$, which are then valiadated by another LLM to verify consistency (see Appendix [14](#sec:app:preference_example){reference-type="ref" reference="sec:app:preference_example"} for a sample pair). The pairs are then split into two sets $\textit{Pairs}_{train}$ and $\textit{Pairs}_{eval}$ for training and evaluation, respectively. We concatenate the generated preference instruction to the example instruction, and augment training and testing data with user preference. During training, we use Equation [\[eq:final_reward\]](#eq:final_reward){reference-type="ref" reference="eq:final_reward"} and the generated preference vector $P$ to calculate reward, but using Equation [\[eq:final_reward_eval\]](#eq:final_reward_eval){reference-type="ref" reference="eq:final_reward_eval"} and $P$ to calculate metrics in the evaluation. More details on rewards are included in Appendix [20](#sec:app:preference_reward_test){reference-type="ref" reference="sec:app:preference_reward_test"}.

#### General tool configuration.

To enhance Orchestrator's generalization abilities, we curate a diverse set of tool configurations to prevent overfitting to specific usage patterns and encourage robust, general-purpose invocation. To emulate heterogeneous user access, we randomize the subset of tools available in each training instance, encouraging Orchestrator to optimize under varying constraints rather than relying on a fixed toolkit. We also vary pricing schedules across training instances to reflect heterogeneous tool costs, exposing the model to different cost configurations so it learns to adapt its optimization strategy as prices change. In aggregate, this approach models the variability in both tool availability and cost structures across users, yielding a richer supervisory signal for optimizing Orchestrator.

# Experimental Setting {#sec:exp_settings}

## Tools {#sec:tools}

In the training, we prepare a large and comprehensive tool set (Appendix [12](#sec:app:tool_train){reference-type="ref" reference="sec:app:tool_train"}), but only sample a subset for each training instance to build diverse tool configurations (§[3.3](#subsec:data_synthesis){reference-type="ref" reference="subsec:data_synthesis"}). We fix the following tool set in the evaluation for fair comparison.

-   **Basic tools.** We use Tavily search API [^1] for web search, Python sandbox for Code interpreter, and build Faiss index with Qwen3-Embedding-8B [@zhang2025qwen3] for local search. Additionally, we also incorporate domain-specific functions, such as `get_flight_status`, to address specialized challenges within those domains.

-   **Specialized LLMs.** We prompt GPT-5 [@gpt-5], GPT-5-mini [@gpt-5] as code writer, employ Qwen2.5-Coder-32B-Instruct [@hui2024qwen2] as another code writer, and leverage Qwen2.5-Math-72B [@yang2024qwen2], Qwen2.5-Math-7B [@yang2024qwen2] as specialized math models.

-   **Generalist LLMs.** We consider GPT-5, GPT-5-mini, Llama-3.3-70B-Instruct [@dubey2024llama], and Qwen3-32B [@yang2025qwen3] as representative generalist models.

## Baselines

We compare Orchestrator-8B produced by ToolOrchestra to baseline orchestrators constructed by prompting LLMs. Additionally, we also compare to off-the-shelf monolithic LLM systems that are (1) not equipped with tools, (2) equipped with basic tools, and (3) using the expanded tool set that further includes specialized expert models and strong generalist models.

For off-the-shelf LLMs, we evaluate GPT-5, Claude Opus 4.1 [@claude41], Llama-3.3-70B-Instruct, Qwen3-235B-A22B [@yang2025qwen3], Llama-3_3-Nemotron-Super-49B-v1 [@bercovich2025llama], Qwen3-8B [@yang2025qwen3].

## Evaluation Configuration

We conduct experiments on three popular benchmarks with complex reasoning: **Humanity's Last Exam (HLE)**, **FRAMES**, and **$\tau^2$-Bench**. Details about these three benchmarks are given in Appendix [10](#sec:app:evaluation_benchmarks){reference-type="ref" reference="sec:app:evaluation_benchmarks"}. Throughout the evaluation, we use the official price for proprietary models and leverage the pricing systems of TogetherAI[^2] for open-source models. We set the inference temperature to 0 and allow maximum 50 turn for Orchestrator to solve a task.

## Training Configuration {#sec:training_config}

We employ Qwen3-8B as the backbone LLM and train it on the GeneralThought-430K [^3] dataset in conjunction with synthetic data ($\S$[3.3](#subsec:data_synthesis){reference-type="ref" reference="subsec:data_synthesis"}). The training configuration uses a learning rate of 1e-6, a maximum input sequence length of 24,000, and a maximum generation length of 8,000, with a training batch size of 16 and a rollout batch size of 8. We allow maximum 50 turns for the Orchestrator to finish a task during rollout and use 16 NVIDIA H100 GPUs throughout the training.

::: table*
::: tabular
@ c p2.9cm c c c c c @ **Tools** & **Model(s)** & **HLE ($\uparrow$)** & **FRAMES ($\uparrow$)** & **$\tau^2$-Bench ($\uparrow$)** & **Cost ($\downarrow$)** & **Latency ($\downarrow$)**\
& [GPT-5]{style="color: gray"} & [35.2]{style="color: gray"} & [--]{style="color: gray"} & [84.2]{style="color: gray"}$^\ddagger$ & [--]{style="color: gray"} & [--]{style="color: gray"}\
& [o3]{style="color: gray"} & [24.3]{style="color: gray"} & [--]{style="color: gray"} & [68.4]{style="color: gray"} & [--]{style="color: gray"} & [--]{style="color: gray"}\
& [GPT-4o]{style="color: gray"} & [5.3]{style="color: gray"} & [--]{style="color: gray"} & [43.8]{style="color: gray"} & [--]{style="color: gray"} & [--]{style="color: gray"}\
& Qwen3-8B & 3.2 & 24.2 & --$^*$ & 0.2 & 0.6\
& Llama-Nemotron-49B & 3.6 & 25.6 & --$^*$ & 0.4 & 1.1\
& Llama-3.3-70B & 3.8 & 32.4 & --$^*$ & 0.5 & 1.4\
& Qwen3-235B-A22B & 5.2 & 34.3 & --$^*$ & 2.6 & 3.3\
& Claude Opus 4.1 & 11.7 & 58.2 & --$^*$ & 27.4 & 8.2\
& GPT-5 & 23.4 & 66.3 & --$^*$ & 6.2 & 4.1\
& Qwen3-8B & 4.7 & 26.5 & 40.7 & 1.3 & 2.2\
& Llama-Nemotron-49B & 6.8 & 28.2 & 23.2 & 2.5 & 3.5\
& Llama-3.3-70B & 4.6 & 42.3 & 17.6 & 2.8 & 4.3\
& Qwen3-235B-A22B & 14.0 & 39.5 & 52.9 & 12.3 & 10.2\
& Claude Opus 4.1 & 19.8 & 63.5 & 46.0 & 76.2 & 32.5\
& GPT-5 & 35.1 & 74.0 & 77.7 & 30.2 & 19.8\
& Qwen3-8B & 30.6 & 68.9 & 72.3 & 27.6 & 18.3\
& Llama-Nemotron-49B & 25.8 & 57.9 & 66.7 & 25.6 & 17.1\
& Llama-3.3-70B & 19.7 & 52.4 & 55.8 & 19.7 & 13.4\
& Qwen3-235B-A22B & 32.8 & 74.2 & 75.6 & 29.7 & 21.2\
& Claude Opus 4.1 & 34.6 & 72.8 & 76.8 & 52.5 & 25.6\
& GPT-5 & 21.2 & 57.5 & 62.3 & 17.8 & 13.6\
&**Orchestrator-8B** & **37.1** & **76.3** & **80.2** & **9.2** & **8.2**\
:::

$^\dagger$ The HLE results of Existing reported SOTA are based on the full set, while other baselines and ours are only on the text-only subset.\
$\ddagger$ Due to implementation differences, we could not fully reproduce GPT-5's reported result (84.2) and only reached 77.7 in our experiments.\
$^*$ $\tau^2$-Bench cannot be solved in the absence of tools.
:::

# Experimental Results

We compare Orchestrator against a wide range of baselines across HLE, FRAMES, and $\tau^2$-Bench. The results are summarized in Table [\[tab:baseline_comparison\]](#tab:baseline_comparison){reference-type="ref" reference="tab:baseline_comparison"}. For simple prompting methods without tools, models such as Qwen3-235B-A22B and Llama-3.3-70B fail to demonstrate strong performance. This highlights the inherent difficulty of the benchmarks, where tool use or additional reasoning mechanisms is essential. Providing tool access improves performance in some cases. For instance, Claude Opus 4.1 with tool usage improves from 11.7 to 19.8 in HLE, and from 58.2 to 63.5 in FRAMES, but at the expense of 2.8x costs and 4x latency. Smaller models like Qwen3-8B perform poorly (4.7 on HLE), indicating that basic tools alone are insufficient. Combining tools with specialized and generalist LLMs generally improves results --- Qwen3-235B-A22B, for example, rises from 14.0 to 32.8 on HLE and from 39.5 to 74.2 on FRAMES, but consumes more than 2 times of cost and latency. However, the gains are inconsistent across different models. GPT-5 using both tools and models suffers from performance drop due to inherent biases, often defaulting to GPT-5-mini (§[6.1](#sec:tool_use_analysis){reference-type="ref" reference="sec:tool_use_analysis"}).

In contrast, our Orchestrator-8B achieves 37.1 on HLE and 76.3 on FRAMES, surpassing all baselines by a large margin. In $\tau^2$-Bench, Orchestrator-8B outperforms GPT-5 using basic tools by 2.5%, exhibiting strong function calling capabilities. Notably, compared to GPT-5 with tool use (35.1 on HLE) and Qwen3-235B-A22B with tool + model (32.8 on HLE), our approach delivers consistent improvements of +2 to +4.3 absolute points, while using only a small fraction of cost and time. These gains are particularly striking given that Orchestrator has only 8B parameters, but is capable of coordinating more intelligent models such as GPT-5, and achieves better performance with lower cost, which highlights the effectiveness of the orchestration strategy. Overall, the results clearly demonstrate the effectiveness of ToolOrchestra and the superiority of Orchestrator model in both performance and efficiency.

# Analysis

## Tool Use Analysis {#sec:tool_use_analysis}

Figure [3](#fig:tool_pies){reference-type="ref" reference="fig:tool_pies"} shows the proportion of calls to each tool when various models serve as the orchestrator to solve a task. Instead of excessively invoking strong models and expensive tools, Orchestrator-8B learns to coordinate them more strategically. For example, in choosing between different models, Claude Opus 4.1 relies on GPT-5 most of the time, while making fewer calls to other models. In contrast, GPT-5 prefers to use GPT-5-mini. Orchestrator-8B learns to choose between various tools strategically, and achieves superior performance while using significantly lower costs.

![The proportion of tool calls made by LLMs to solve a task (averaged across HLE, Frames and $\tau^2$-bench). Qwen-32B refers to Qwen3-32B [@yang2025qwen3] and Coder-32B refers to Qwen2.5-Coder-32B-Instruct [@hui2024qwen2]. Compared to other strong foundation models, Orchestrator-8B makes more balanced tool calls, and does not exhibit strong biases toward a particular tool or model. Detailed statistics are shown in Table [\[tab:tool_analysis_full\]](#tab:tool_analysis_full){reference-type="ref" reference="tab:tool_analysis_full"}. ](figs/tool_pies.pdf){#fig:tool_pies width="\\linewidth"}

## Cost Analysis {#sec:cost_analysis}

::: wrapfigure
r0.4 ![image](figs/cost_performance.pdf){width="0.35\\columnwidth"}

[]{#fig:cost_effectiveness label="fig:cost_effectiveness"}
:::

To analyze the cost-effectiveness, we display the performance on HLE as a function of cost in Figure [\[fig:cost_effectiveness\]](#fig:cost_effectiveness){reference-type="ref" reference="fig:cost_effectiveness"}. We experiment with settings where the maximum number of 10, 20, 50 and 100 turns are allowed to finish a task. As the maximum number of allowed turns increases (i.e., cost increases), all models show improved performance. Orchestrator-8B consistently outperforms GPT-5, Claude Opus 4.1 and Qwen3-235B-A22B at a given budget, and can achieve similar results at a substantially lower cost. This demonstrates the capability of Orchestrator-8B to manage a heterogeneous set of tools, and pushes the intelligence boundary of the system as a whole.

## Generalization {#sec:main:generalization}

To evaluate Orchestrator-8B's generalization capability, we test it with a tool configuration containing models unseen during training: (1) Query writer: Claude Opus 4.1, o3-mini and GPT-4o [@gpt-4o]; (2) Code writer: Claude Opus 4.1, Claude Sonnet 4.1 and Codestral-22B-v0.1 [@codestral]; (3) Math model: OpenMath-Llama-2-70b [@toshniwal2024openmath], DeepSeek-Math-7b-Instruct [@shao2024deepseekmath]; (4) Generalist Models: Claude Opus 4.1, Claude Sonnet 4.1 and Gemma-3-27b-it [@team2025gemma].

::: wraptable
r0.5
:::

We keep the basic tools (web search, local search and code interpreter) as the same mentioned in §[4.1](#sec:tools){reference-type="ref" reference="sec:tools"} and generate model descriptions following the same procedures mentioned in section §[3.1](#sec:unified_tool_call){reference-type="ref" reference="sec:unified_tool_call"}. Table [\[tab:model_generalization\]](#tab:model_generalization){reference-type="ref" reference="tab:model_generalization"} demonstrates that Orchestrator-8B shows strong skills in using models as tools. Even provided with a set of models not seen during training, Orchestrator successfully adapts to it by understanding their skills and weaknesses from model descriptions, and consistently achieves the best performance at the lowest cost across HLE, Frames and $\tau^2$-Bench. This confirms that the diverse tool configurations during training effectively enhance the generalization capabilities of Orchestrator-8B. In Appendix [16](#sec:app:generalization_pricing){reference-type="ref" reference="sec:app:generalization_pricing"}, we conduct further experiments to evaluate Orchestrator-8B on pricing configurations unseen in training.

## User Preferences

::: wraptable
r0.45
:::

To assess Orchestrator-8B's ability to adapt to heterogeneous user preferences at test time, we evaluate it on the Preference-aware test set described in §[3.3](#subsec:data_synthesis){reference-type="ref" reference="subsec:data_synthesis"}, where we concatenate each question with an additional preference instruction. We evaluate the model preference adherence performance by calculating the preference-aware rewards defined in Appendix [20](#sec:app:preference_reward_test){reference-type="ref" reference="sec:app:preference_reward_test"}. Table [\[tab:preference\]](#tab:preference){reference-type="ref" reference="tab:preference"} shows that, even strong monolithic systems such as GPT-5 struggle to faithfully follow user preferences. In contrast, Orchestrator-8B exhibits remarkably better adherence to user preferences.

# Related Work {#sec:related_work}

## From Tool Learning to Generalist Agents

Tool learning underpins advanced reasoning in LLMs, as many tasks require external APIs, search engines, or code interpreters. Early work [@schick2023toolformer; @qintoolllm; @qian2024tell] used supervised fine-tuning (SFT) on tool-labeled data like GPT-4 generated dialogues. More recently, tool use has been framed as a sequential decision-making problem optimized by RL, with systems such as WebGPT [@nakano2021webgpt], Search-R1 [@jin2025search], ToRL [@li2025torl], StepTool [@yu2024steptool], SWiRL [@goldie2025synthetic], Nemotron-Research-Tool-N1 [@zhang2025nemotron], and ToolRL [@qian2025toolrl]. Building on this foundation, generalist agents like deep research agents [@openai_deep_research_2025; @deepmind_gemini_deep_research_2025; @perplexity_deep_research_2025; @moonshot_kimi_researcher_2025] autonomously discover, analyze, and synthesize across sources to produce analyst-level reports, aligning with the vision of compound AI systems [@compound-ai-blog; @chaudhry2025towards]. Recent open-source frameworks like SmolAgent [@smolagents], WebAgent [@li2025websailor; @wu2025webdancer; @tao2025webshaper], OWL [@hu2025owl], AutoAgent [@tang2025autoagent], and OAgent [@zhu2025oagents] extend this trend toward modular, robust, and accessible systems, highlighting the broader democratization of generalist agents.

## From Tool-Use Accuracy to Efficiency and Controllability

Beyond correctness, recent work emphasizes efficiency and controllability, aiming to reduce computational costs and better align outputs with user preferences. Prompting-based methods like Self Divide-and-Conquer [@wang2025self], Efficient Agents [@wang2025efficient], and SMART [@qian2025smart] adaptively invoke tools or fine-tune usage, though they often depend on heavy prompt engineering or curated datasets. RL provides a more flexible alternative, where reward shaping balances accuracy, efficiency, and reliability. Advances include integrating auxiliary signals (e.g., response length, task difficulty)[@aggarwal2025l1; @arora2025training; @wang2025harnessing] and combining verifiable signals with human feedback[@peng2025agentic]. A related direction is weak-to-strong generalization [@burns2024weak], which explores eliciting stronger models from weaker supervision. The most relevant work, OTC [@wang2025otc], improves efficiency by penalizing excessive calls while preserving accuracy. Unlike the prior work, our approach addresses the broader orchestration problem by using RL to coordinate diverse tools and models, balancing correctness, efficiency, and user preference for finer alignment and more robust deployment.

# Conclusion

In this work, we presented ToolOrchestra, a method for training a small orchestration model to unify diverse tools and specialized models. By training Orchestrator end-to-end with reinforcement learning, we showed that it can learn to plan adaptive tool-use strategies guided by both outcome quality, efficiency, and human preference rewards. This enables the agent to dynamically balance performance and cost, rather than relying on static heuristics or purely supervised approaches. To aid reinforcement learning, we also contribute a complex user-agent-tool synthetic dataset ToolScale. Our experiments on challenging benchmarks demonstrate that our Orchestrator-8B attains state-of-the-art performance while operating at significantly lower cost compared to larger models. Looking ahead, we envision more sophisticated recursive orchestrator systems to push the upper bound of intelligence but also to further enhance efficiency in solving increasingly complex agentic tasks.

# Pilot Study {#sec:app:pilot_study}

To evaluate the effectiveness of simple prompting as a method to configure an off-the-shelf language model to act as an orchestrator, we prompted GPT-5 and Qwen3-8B with a similar setting and the same prompt template we used in Section [4](#sec:exp_settings){reference-type="ref" reference="sec:exp_settings"}, allowing them to use GPT-5, GPT-5-mini, Qwen3-32B, and Qwen2.5-Coder-32B as tools and instruct the orchestrator to achieve best results while maintaining lowest cost. We then ran the model on a set of 300 HLE problems with max_tokens=32,000 and temperature T=0 and monitored the average number of times each model referred to one of its model choices. The results are shown in Figure [\[fig:imbalanced-tool-calls\]](#fig:imbalanced-tool-calls){reference-type="ref" reference="fig:imbalanced-tool-calls"}. When Qwen3-8B serves as the orchestrator, it exhibits a strong tendency to delegate the task to GPT-5 (73% of the cases). We refer to this phenomenon as self-enhancement bias [@zheng2023judging], where the orchestrator favors its variants. In contrast, when GPT-5 serves as the orchestrator, it prefers to call GPT-5 or GPT-5-mini in 98% of the cases. We term this phenomenon other-enhancement bias, where the orchestrator favors stronger models regardless of cost considerations, even though humans instruct them to do so.

Such imbalanced invocation patterns highlight the limitations of using off-the-shelf language models as orchestrators by simple prompting: their decisions are heavily biased rather than balanced across available options, resulting in poor orchestration effectiveness. This observation motivates our method ToolOrchestra to train a dedicated small orchestrator to decide when and how to invoke more intelligent language models.

# Evaluation Benchmarks {#sec:app:evaluation_benchmarks}

-   **Humanity's Last Exam (HLE)** [@phan2025humanity]. A large-scale benchmark comprising PhD-level questions across mathematics, humanities, natural sciences and more. It evaluates the model capabilities to perform iterative search and intensive reasoning. Questions are multiple-choice or short-answer, with 10--14% requiring images. We use the text-only subset, designed to be unambiguous and not solvable by simple web search.

-   **FRAMES** [@krishna2024factfetchreasonunified]. A dataset for end-to-end evaluation of retrieval-augmented generation (RAG), covering factuality, retrieval accuracy, and reasoning. It contains 824 multi-hop questions requiring 2--15 Wikipedia articles, spanning numerical, tabular, temporal, and multi-constraint reasoning.

-   **$\tau^2$-Bench** [@barres2025tau]. A benchmark to evaluate model capabilities to use tools and solve problems in conversations with users. It includes tasks in three domains: telecom, retail and airline.

# Model description for Qwen3-32B {#sec:app:model_description}

The model shows advanced mathematical and quantitative reasoning, often solving complex problems and only faltering on highly specialized or computationally heavy items. Scientific domain knowledge is strong---especially in biology---with solid performance in physics and engineering; chemistry is mixed, with notable weaknesses in exact nomenclature and InChI outputs. Logical problem-solving is high, while humanities knowledge is moderate and uneven, with gaps in niche scholarly details. Coding and function call abilities are moderate, where it makes mistakes in parameters from time to time. Overall, the model has broad knowledge and robust analytic skills, but accuracy drops on narrow, recent, or rote-precision tasks, particularly in chemical informatics.

# Tools in training {#sec:app:tool_train}

Below is the complete list of tools used in the training. For each example rollout, we randomly sample a subset of them to simulate heterogeneous availability of tools:

-   Query writer: GPT-5 [@gpt-5], GPT-5-mini [@gpt-5], meta-llama/Llama-3.3-70B-Instruct [@dubey2024llama], meta-llama/Llama-3.1-8B-Instruct [@dubey2024llama], deepseek-ai/DeepSeek-R1 [@guo2025deepseek], nvidia/Llama-3_1-Nemotron-Ultra-253B-v1 [@bercovich2025llama], microsoft/Phi-4-mini-instruct [@abouelenin2025phi], google/gemma-3-27b-it [@team2025gemma], Qwen/Qwen3-32B [@yang2025qwen3]

-   Web search: We use Tavily search API [^4] to provide orchestrator real-time web access.

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
Preference vector: $P$ = \[0,1,1,1,0,0,0,0,0\] Explanation: The first digit in the preference vector corresponds to the first tool in $T$; The second digit in the preference vector corresponds to the second tool in $T$, etc. The last three digits in $P$ corresponds to accuracy, cost and latency, aligned with the definitions in §[3.2](#sec:end2endRL){reference-type="ref" reference="sec:end2endRL"}. Therefore, this preference vector means the user prefers to use local search, Qwen/Qwen3-235B-A22B, meta-llama/Llama-3.3-70B-Instruct.

# Use of LLMs Disclosure

We used GPT-5 to polish the writing, primarily in the Abstract, Introduction, Methodology, and Experiments sections, to improve the grammar, clarity, and readability. The research ideas, methodology, experiments, and analyses were entirely conducted by the authors.

# Generalization of pricing configurations {#sec:app:generalization_pricing}

In Section [6.3](#sec:main:generalization){reference-type="ref" reference="sec:main:generalization"}, we examined Orchestrator-8B's ability to generalize to unseen tools. Here, we investigate its generalization across heterogeneous pricing regimes, where the same tools are assigned different costs. We evaluate whether the model adapts by adjusting its tool-calling strategy to optimize outcomes, efficiency, and alignment with user preferences---reflecting realistic settings in which tool costs vary across users. We test Orchestrator-8B under a pricing configuration not encountered during training. Specifically, we use the pricing configuration from deepinfra[^5]. As shown in Table [\[tab:generalization_pricing_config\]](#tab:generalization_pricing_config){reference-type="ref" reference="tab:generalization_pricing_config"}, it consistently delivers superior performance, cost efficiency, and accuracy. These results demonstrate that training with diverse pricing configurations produces a model that is not constrained to a particular tool setup and can robustly generalize across diverse user scenarios.

# Data Synthesis {#sec:app:data_synthesis}

#### ToolScale.

To enable end-to-end RL training of Orchestrator, we require data involving user-agent-tool interaction trajectories, but such verifiable data is scarce. To generate such high-quality data, we devise a two-step process: (1) simulating rich user-agent-tool environments, including creating database schemas and tool APIs; and (2) based on the environment, generating diverse user tasks together with their corresponding ground truth solutions. We further ensure quality by carefully verifying that each task is solvable using the provided databases and tool APIs. Figure [2](#fig:data_synthesis){reference-type="ref" reference="fig:data_synthesis"} provided an overview of this process. Firstly, to simulate real-world user-agent-tool environments scalably, we choose a domain $D$ and then ask an LLM to generate a database which includes schema, major subjects to focus on and database entries (as illustrated in the top-left of Figure [2](#fig:data_synthesis){reference-type="ref" reference="fig:data_synthesis"}). Each entry is then checked to ensure coherence, adherence to the schema, and consistency across content, logic, and entities. Based on the given domain $D$, LLM proposes frequently-used tools. Secondly, to increase the diversity of the task instructions, LLM first proposes diverse intents frequently seen in domain $D$, which are later converted to specific tasks based on detailed database information. Each generated task consists of task instruction $I$, gold function calls $A={a_1, a_2, ..., a_l}$, and short information $o$ that must be mentioned during the process to solve the task. To enhance the difficulty of the generated tasks, we leverage an additional LLM to complicate tasks by adding more complexities such as more constraints.

To ensure the quality of the synthesized data, we filter the data to remove a task if: (1) the execution of golden function calls reports an error; (2) LLMs cannot solve it in pass@$8$; and (3) the task can be solved without any actions. In Appendix [18](#sec:app:details_of_toolscale){reference-type="ref" reference="sec:app:details_of_toolscale"}, we list the statistics of the generated data in each domain. More examples and prompts used to synthesize data can be found in Appendix [19](#sec:app:data_synthesis_prompts){reference-type="ref" reference="sec:app:data_synthesis_prompts"}. To evaluate whether a trajectory $\tau$ solves the given task, we define the following criteria: (1) *execution correctness*, namely whether the database content matches after executing the golden function calls $A$ and the trajectory $\tau$; (2) *process fidelity*, i.e., whether the predefined information $o$, which is required to be communicated in the process to solve the task, is mentioned in $\tau$; (3) *operation completeness*, that is whether the database entries operated in the ground truth trajectory $A$ are also operated in $\tau$. We consider $\tau$ solves the task if all of three criteria are satisfied, or fails otherwise.

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

# Breakdown of ToolScale {#sec:app:details_of_toolscale}

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

During training, we directly follow the Equation [\[eq:final_reward\]](#eq:final_reward){reference-type="ref" reference="eq:final_reward"} to calculate rewards. In the evaluation, we use the following procedure. Following the definition in §[3.2](#sec:end2endRL){reference-type="ref" reference="sec:end2endRL"}, we have a tool set $\left\{t_1, t_2, ..., t_n\right\}$ and a rollout trajectory $\tau$, we consider the vector $M^{\tau}=[m^{\tau}_{t_1}, m^{\tau}_{t_2}, \ldots, m^{\tau}_{t_n},r^{\tau}_\text{outcome},r^{\tau}_\text{compute},r^{\tau}_\text{latency}]$, where $m^{\tau}_{t_\bullet}$ is the number of times tool $t_\bullet$ is invoked in $\tau$. In the evaluation, we obtain the baseline vector $M_0$ by running the starting checkpoint, e.g., Qwen3-8B. For example, if we would like to evaluate a checkpoint $\mathit{CKPT}_s$ that is trained for $s$ steps from a base Qwen3-8B model, then we first run Qwen3-8B on the benchmark and record the vector $M^{\tau(e)}_0$ as the baseline vector for the Qwen3-8B's trajectory $\tau(e)$ for each example $e$ of the benchmark. We then obtain $M^{\tau(e)}_s$ by running $\mathit{CKPT}_s$ on the same example $e$. $M^{\tau(e)}_s$ is normalized as $$M^{{\tau(e)}}_{\text{normalized}, s}[k] = 
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

[^2]: <https://www.together.ai/pricing>

[^3]: <https://huggingface.co/datasets/natolambert/GeneralThought-430K-filtered>

[^4]: <https://www.tavily.com/>

[^5]: https://deepinfra.com
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
