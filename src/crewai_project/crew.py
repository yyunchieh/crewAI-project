from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
import os
import yaml
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Raproject():
    """Raproject crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    topic: str

    def __init__(self, *args, **kwargs):

        base_dir = os.path.dirname(os.path.abspath(__file__))  
        config_dir = os.path.join(base_dir, "config")       

        with open(os.path.join(config_dir, "tasks.yaml"), "r", encoding="utf-8") as f:
            self.tasks_config = yaml.safe_load(f)

        with open(os.path.join(config_dir, "agents.yaml"), "r", encoding="utf-8") as f:
            self.agents_config = yaml.safe_load(f)["agents"]

        print("agents_config keys:", self.agents_config.keys())

        self.agents = [self.researcher(), self.analyst(), self.writer()]
        self.tasks = [self.research_task(), self.analysis_task(), self.reporting_task()]



    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    
    @agent
    def researcher(self) -> Agent:
        print("Inside researcher(), agents_config keys:", self.agents_config.keys())
        return Agent(
            config=self.agents_config['researcher'], # type: ignore[index]
            verbose=True
        )

    @agent
    def analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['analyst'], # type: ignore[index]
            verbose=True
        )
    
    @agent
    def writer(self) -> Agent:
        return Agent(
            config=self.agents_config['writer'], # type: ignore[index]
            verbose=True
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def research_task(self) -> Task:
        task_conf = self.tasks_config['tasks']['research_task'].copy()
        agent_key = task_conf.pop('agent')
        return Task(
            config=task_conf,
            agent=getattr(self, agent_key)(),
            input_values={'topic': '{{ topic }}'}
        )

    @task
    def analysis_task(self) -> Task:
        task_conf = self.tasks_config['tasks']['analysis_task']
        agent_key = task_conf.pop('agent')
        return Task(
            config=task_conf,
            agent=getattr(self, agent_key)(),
            input_values={'topic': '{{ topic }}'}
        )


    @task
    def reporting_task(self) -> Task:
        task_conf = self.tasks_config['tasks']['reporting_task'].copy()
        agent_key = task_conf.pop('agent')
        return Task(
            config=task_conf,
            agent=getattr(self, agent_key)(),
            input_values={'topic': '{{ topic }}'},
            output_file='report.md'
        )


    @crew
    def crew(self) -> Crew:
        """Creates the Raproject crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
           agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
