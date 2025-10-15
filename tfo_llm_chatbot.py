import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from dataclasses import dataclass, asdict
import asyncio
import ollama
import re

logger = logging.getLogger(__name__)

@dataclass
class Employee:
    employee_id: str
    name: str
    email: str
    current_status: str
    current_project: Optional[str]
    project_end_date: Optional[date]
    bench_start_date: Optional[date]
    skills: List[Dict]
    performance_rating: float
    location: str
 
@dataclass
class Requisition:
    requisition_id: str
    project_name: str
    role_title: str
    status: str
    start_date: date
    required_skills: List[Dict]
    location: str
    experience_level: str
    hiring_type: str

class GenAIChatbot:
    def __init__(self, model_name: str = "llama3.2:latest"):
        self.employees = self._load_mock_employees()
        self.requisitions = self._load_mock_requisitions()
        self.skill_ontology = self._load_skill_ontology()
        self.model_name = model_name
        self.ollama_client = ollama.Client()

        # Define agent types and their capabilities
        self.agents = {
            "employee_advisor": {
                "description": "Helps employees find suitable positions and career opportunities",
                "capabilities": ["find_positions", "skill_analysis", "career_guidance"]
            },
            "staffing_consultant": {
                "description": "Assists managers in finding suitable employees for open positions",
                "capabilities": ["employee_search", "skill_matching", "staffing_recommendations"]
            },
            "skill_analyst": {
                "description": "Analyzes skill gaps and provides training recommendations",
                "capabilities": ["skill_gap_analysis", "training_recommendations"]
            },
            "general_assistant": {
                "description": "Handles general queries and routing",
                "capabilities": ["greeting", "routing", "basic_info"]
            }
        }

    def _load_mock_employees(self) -> List[Employee]:
        """Load mock employee data"""
        return [
            Employee(
                employee_id="EMP001",
                name="Raj Sharma",
                email="raj.sharma@zensar.com",
                current_status="BENCH",
                current_project=None,
                project_end_date=None,
                bench_start_date=date(2024, 4, 15),
                skills=[
                    {"skill_name": "Java", "category": "Backend", "experience_years": 6, "proficiency_level": "EXPERT"},
                    {"skill_name": "Spring Boot", "category": "Backend", "experience_years": 5, "proficiency_level": "ADVANCED"},
                    {"skill_name": "React", "category": "Frontend", "experience_years": 2, "proficiency_level": "INTERMEDIATE"},
                    {"skill_name": "SQL", "category": "Database", "experience_years": 4, "proficiency_level": "ADVANCED"},
                    {"skill_name": "Angular", "category": "Frontend", "experience_years": 1, "proficiency_level": "BEGINNER"}
                ],
                performance_rating=4.2,
                location="Pune"
            ),
            Employee(
                employee_id="EMP002",
                name="Priya Patel",
                email="priya.patel@zensar.com",
                current_status="TRANSITIONING",
                current_project="Project Phoenix",
                project_end_date=date(2024, 6, 30),
                bench_start_date=None,
                skills=[
                    {"skill_name": "Java", "category": "Backend", "experience_years": 7, "proficiency_level": "EXPERT"},
                    {"skill_name": "React", "category": "Frontend", "experience_years": 3, "proficiency_level": "ADVANCED"},
                    {"skill_name": "Angular", "category": "Frontend", "experience_years": 4, "proficiency_level": "ADVANCED"},
                    {"skill_name": "Node.js", "category": "Backend", "experience_years": 2, "proficiency_level": "INTERMEDIATE"},
                    {"skill_name": "MongoDB", "category": "Database", "experience_years": 3, "proficiency_level": "ADVANCED"}
                ],
                performance_rating=4.5,
                location="Bangalore"
            ),
            Employee(
                employee_id="EMP003",
                name="Amit Kumar",
                email="amit.kumar@zensar.com",
                current_status="ACTIVE",
                current_project="Project Alpha",
                project_end_date=date(2024, 8, 15),
                bench_start_date=None,
                skills=[
                    {"skill_name": "Python", "category": "Backend", "experience_years": 5, "proficiency_level": "ADVANCED"},
                    {"skill_name": "Django", "category": "Backend", "experience_years": 4, "proficiency_level": "ADVANCED"},
                    {"skill_name": "React", "category": "Frontend", "experience_years": 2, "proficiency_level": "INTERMEDIATE"},
                    {"skill_name": "PostgreSQL", "category": "Database", "experience_years": 4, "proficiency_level": "ADVANCED"}
                ],
                performance_rating=4.0,
                location="Hyderabad"
            ),
            Employee(
                employee_id="EMP004",
                name="Sneha Desai",
                email="sneha.desai@zensar.com",
                current_status="BENCH",
                current_project=None,
                project_end_date=None,
                bench_start_date=date(2024, 5, 1),
                skills=[
                    {"skill_name": "Java", "category": "Backend", "experience_years": 8, "proficiency_level": "EXPERT"},
                    {"skill_name": "Spring Boot", "category": "Backend", "experience_years": 6, "proficiency_level": "EXPERT"},
                    {"skill_name": "Angular", "category": "Frontend", "experience_years": 5, "proficiency_level": "ADVANCED"},
                    {"skill_name": "SQL", "category": "Database", "experience_years": 6, "proficiency_level": "EXPERT"},
                    {"skill_name": "AWS", "category": "Cloud", "experience_years": 3, "proficiency_level": "INTERMEDIATE"}
                ],
                performance_rating=4.7,
                location="Pune"
            ),
            Employee(
                employee_id="EMP005",
                name="Varun Singh",
                email="varun.singh@zensar.com",
                current_status="NOTICE_PERIOD",
                current_project="Project Beta",
                project_end_date=date(2024, 6, 15),
                bench_start_date=None,
                skills=[
                    {"skill_name": "React", "category": "Frontend", "experience_years": 4, "proficiency_level": "ADVANCED"},
                    {"skill_name": "JavaScript", "category": "Frontend", "experience_years": 5, "proficiency_level": "ADVANCED"},
                    {"skill_name": "Node.js", "category": "Backend", "experience_years": 3, "proficiency_level": "INTERMEDIATE"},
                    {"skill_name": "Java", "category": "Backend", "experience_years": 2, "proficiency_level": "INTERMEDIATE"}
                ],
                performance_rating=3.8,
                location="Chennai"
            )
        ]

    
    def _load_mock_requisitions(self) -> List[Requisition]:
        """Load mock requisition data"""
        return [
            Requisition(
                requisition_id="REQ001",
                project_name="Digital Banking Platform",
                role_title="Full Stack Developer",
                status="OPEN",
                start_date=date(2024, 6, 1),
                required_skills=[
                    {"skill_name": "Java", "min_experience": 5, "required_level": "ADVANCED", "is_mandatory": True},
                    {"skill_name": "Spring Boot", "min_experience": 3, "required_level": "ADVANCED", "is_mandatory": True},
                    {"skill_name": "React", "min_experience": 2, "required_level": "INTERMEDIATE", "is_mandatory": True},
                    {"skill_name": "SQL", "min_experience": 3, "required_level": "ADVANCED", "is_mandatory": False}
                ],
                location="Pune",
                experience_level="Senior",
                hiring_type="INTERNAL"
            ),
            Requisition(
                requisition_id="REQ002",
                project_name="E-commerce Modernization",
                role_title="Frontend Lead",
                status="OPEN",
                start_date=date(2024, 6, 15),
                required_skills=[
                    {"skill_name": "React", "min_experience": 4, "required_level": "ADVANCED", "is_mandatory": True},
                    {"skill_name": "Angular", "min_experience": 3, "required_level": "ADVANCED", "is_mandatory": True},
                    {"skill_name": "JavaScript", "min_experience": 5, "required_level": "EXPERT", "is_mandatory": True},
                    {"skill_name": "TypeScript", "min_experience": 2, "required_level": "INTERMEDIATE", "is_mandatory": False}
                ],
                location="Bangalore",
                experience_level="Lead",
                hiring_type="BOTH"
            ),
            Requisition(
                requisition_id="REQ003",
                project_name="Healthcare Analytics",
                role_title="Backend Developer",
                status="OPEN",
                start_date=date(2024, 7, 1),
                required_skills=[
                    {"skill_name": "Python", "min_experience": 4, "required_level": "ADVANCED", "is_mandatory": True},
                    {"skill_name": "Django", "min_experience": 3, "required_level": "ADVANCED", "is_mandatory": True},
                    {"skill_name": "PostgreSQL", "min_experience": 3, "required_level": "ADVANCED", "is_mandatory": True},
                    {"skill_name": "AWS", "min_experience": 2, "required_level": "INTERMEDIATE", "is_mandatory": False}
                ],
                location="Hyderabad",
                experience_level="Mid-Senior",
                hiring_type="INTERNAL"
            ),
            Requisition(
                requisition_id="REQ004",
                project_name="Insurance Portal",
                role_title="Java Full Stack Developer",
                status="OPEN",
                start_date=date(2024, 6, 10),
                required_skills=[
                    {"skill_name": "Java", "min_experience": 6, "required_level": "EXPERT", "is_mandatory": True},
                    {"skill_name": "Spring Boot", "min_experience": 4, "required_level": "ADVANCED", "is_mandatory": True},
                    {"skill_name": "Angular", "min_experience": 3, "required_level": "ADVANCED", "is_mandatory": True},
                    {"skill_name": "SQL", "min_experience": 4, "required_level": "ADVANCED", "is_mandatory": True},
                    {"skill_name": "React", "min_experience": 2, "required_level": "INTERMEDIATE", "is_mandatory": False}
                ],
                location="Pune",
                experience_level="Senior",
                hiring_type="INTERNAL"
            )
        ]
    
    def _load_skill_ontology(self) -> Dict:
        """Load skill relationships and categories"""
        return {
            "Java": {"category": "Backend", "related_skills": ["Spring Boot", "J2EE", "Microservices"]},
            "Spring Boot": {"category": "Backend", "related_skills": ["Java", "Microservices", "REST API"]},
            "React": {"category": "Frontend", "related_skills": ["JavaScript", "TypeScript", "Redux"]},
            "Angular": {"category": "Frontend", "related_skills": ["TypeScript", "JavaScript", "RxJS"]},
            "Python": {"category": "Backend", "related_skills": ["Django", "Flask", "FastAPI"]},
            "SQL": {"category": "Database", "related_skills": ["Database Design", "Query Optimization"]}
        }

    async def select_agent(self, query: str, user_role: str, employee_id: Optional[str] = None) -> Dict:
        """Use LLM to intelligently select the most appropriate agent"""
        
        system_prompt = """You are an intelligent agent selector for a Talent Management chatbot. 
        Analyze the user query and select the most appropriate agent to handle it.

        Available Agents:
        1. employee_advisor - For employees seeking positions, career guidance, skill matching
        2. staffing_consultant - For managers searching for employees, staffing needs
        3. skill_analyst - For skill analysis, gap identification, training recommendations
        4. general_assistant - For greetings, basic questions, routing

        Respond with a JSON object containing:
        - selected_agent: the chosen agent name
        - confidence: confidence score (0-1)
        - reasoning: brief explanation
        - required_data: list of data needed from our system
        """

        user_context = f"""
        User Role: {user_role}
        Query: {query}
        Employee ID: {employee_id if employee_id else 'Not provided'}
        """

        try:
            response = self.ollama_client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_context}
                ],
                format="json"
            )
            
            agent_selection = json.loads(response['message']['content'])
            return agent_selection
            
        except Exception as e:
            logger.error(f"Error in agent selection: {str(e)}")
            # Fallback to rule-based selection
            return self._fallback_agent_selection(query, user_role)

    def _fallback_agent_selection(self, query: str, user_role: str) -> Dict:
        """Fallback agent selection when LLM fails"""
        query_lower = query.lower()
        
        if user_role in ["EMPLOYEE", "CONSULTANT"]:
            if any(term in query_lower for term in ["position", "job", "opportunity", "role", "project"]):
                return {"selected_agent": "employee_advisor", "confidence": 0.8, "reasoning": "Employee seeking positions"}
            elif any(term in query_lower for term in ["skill", "training", "learn", "improve"]):
                return {"selected_agent": "skill_analyst", "confidence": 0.7, "reasoning": "Skill-related query"}
        
        elif user_role in ["MANAGER", "TSC_CONSULTANT"]:
            if any(term in query_lower for term in ["find", "search", "employee", "resource", "staff"]):
                return {"selected_agent": "staffing_consultant", "confidence": 0.9, "reasoning": "Staffing search query"}
        
        return {"selected_agent": "general_assistant", "confidence": 0.6, "reasoning": "General query"}

    async def process_query(self, user_role: str, query: str, employee_id: Optional[str] = None) -> Dict:
        """Main method to process any user query using GenAI"""
        
        # Step 1: Select appropriate agent
        agent_selection = await self.select_agent(query, user_role, employee_id)
        selected_agent = agent_selection["selected_agent"]

        print('selected agent', selected_agent)
        
        # Step 2: Get relevant context data
        context_data = await self._gather_context_data(query, user_role, employee_id)
        
        print("context_data", context_data)
        # Step 3: Process with selected agent
        
        if selected_agent == "employee_advisor":
            response = await self._process_employee_advisor(query, context_data)
        elif selected_agent == "staffing_consultant":
            response = await self._process_staffing_consultant(query, context_data)
        elif selected_agent == "skill_analyst":
            response = await self._process_skill_analyst(query, context_data)
        else:
            response = await self._process_general_assistant(query, context_data)
        
        # Add agent metadata to response
        response["agent_metadata"] = agent_selection
        response["selected_agent"] = selected_agent
        
        return response

    async def _gather_context_data(self, query: str, user_role: str, employee_id: Optional[str]) -> Dict:
        """Gather relevant data based on query analysis"""
        
        context = {
            "query": query,
            "user_role": user_role,
            "employee_id": employee_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # Use LLM to determine what data is needed
        system_prompt = """Analyze the query and determine what data is needed from our system.
        Available data types:
        - employee_data: Employee profiles, skills, status
        - requisition_data: Open positions, requirements
        - skill_ontology: Skill relationships, categories
        - matching_data: Pre-calculated matches
        
        Respond with JSON: {"needed_data": ["data_type1", "data_type2"]}
        """
        
        try:
            response = self.ollama_client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Query: {query}, User Role: {user_role}"}
                ],
                format="json"
            )
            
            data_needs = json.loads(response['message']['content'])
            
            # Gather the requested data
            # if "employee_data" in data_needs.get("needed_data", []):
            if employee_id:
                context["employee"] = next((emp for emp in self.employees if emp.employee_id == employee_id), None)
            else:
                context["all_employees"] = self.employees
            
            if "requisition_data" in data_needs.get("needed_data", []):
                context["requisitions"] = [req for req in self.requisitions if req.status == "OPEN"]
            
            if "skill_ontology" in data_needs.get("needed_data", []):
                context["skill_ontology"] = self.skill_ontology
                
        except Exception as e:
            logger.error(f"Error gathering context: {str(e)}")
            # Fallback: gather all relevant data
            context.update(self._fallback_data_gathering(query, user_role, employee_id))

        # Ensure that if an employee_id was provided we include that employee in context
        # even if the LLM did not explicitly request employee_data. This prevents
        # downstream AttributeError when code assumes an employee object is present.
        # if employee_id and "employee" not in context:
        #     context["employee"] = next((emp for emp in self.employees if emp.employee_id == employee_id), None)
        
        return context

    def _fallback_data_gathering(self, query: str, user_role: str, employee_id: Optional[str]) -> Dict:
        """Fallback data gathering when LLM fails"""
        data = {}
        query_lower = query.lower()
        
        if user_role in ["EMPLOYEE", "CONSULTANT"]:
            if employee_id:
                data["employee"] = next((emp for emp in self.employees if emp.employee_id == employee_id), None)
            data["requisitions"] = [req for req in self.requisitions if req.status == "OPEN"]
            
        elif user_role in ["MANAGER", "TSC_CONSULTANT"]:
            if any(term in query_lower for term in ["find", "search", "employee"]):
                data["all_employees"] = self.employees
                data["skill_ontology"] = self.skill_ontology
        
        return data

    async def _process_employee_advisor(self, query: str, context: Dict) -> Dict:
        """Process queries using Employee Advisor agent"""
        
        employee = context.get("employee")
        requisitions = context.get("requisitions", [])
        
        system_prompt = """You are an Employee Career Advisor. Help employees find suitable positions and provide career guidance.

        Available data:
        - Employee profile with skills, experience, status
        - Open positions with requirements
        - Skill ontology for career pathing

        Provide:
        1. Personalized position recommendations
        2. Match analysis with reasoning
        3. Career advice and next steps
        4. Skill development suggestions

        Be encouraging and professional.
        """
        
        user_prompt = f"""
        Employee: {employee.name if employee else 'Unknown'}
        Current Status: {employee.current_status if employee else 'Unknown'}
        Skills: {json.dumps(employee.skills, default=str) if employee else 'No data'}
        
        Open Positions: {json.dumps([asdict(req) for req in requisitions], default=str)}
        
        Employee Query: {query}
        
        Please provide personalized recommendations and analysis.
        """
        
        try:

            response = self.ollama_client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            llm_response = response['message']['content']
            print('this is the final llm_response', llm_response)
            
            # Enhanced with structured data
            # structured_matches = await self._find_enhanced_matches(employee, requisitions)
            # print('structured_matches', structured_matches)

            return {
                "type": "employee_advisor_response",
                "llm_response": llm_response,
                # "structured_data": structured_matches
                # "recommendations": self._generate_ai_recommendations(employee, requisitions),
                # "action_items": self._extract_action_items(llm_response)
            }
            
        except Exception as e:
            logger.error(f"Error in employee advisor: {str(e)}")
            return await self._fallback_employee_processing(query, context)

    async def _process_staffing_consultant(self, query: str, context: Dict) -> Dict:
        """Process queries using Staffing Consultant agent"""
        
        employees = context.get("all_employees", [])
        requisitions = context.get("requisitions", [])
        
        system_prompt = """You are a Staffing Consultant. Help managers find suitable employees for open positions.

        Available data:
        - Employee database with skills, availability, performance
        - Open positions with detailed requirements
        - Skill matching capabilities

        Provide:
        1. Best-fit employee recommendations
        2. Detailed match analysis
        3. Availability assessment
        4. Staffing strategy recommendations

        Be analytical and business-focused.
        """
        
        user_prompt = f"""
        Available Employees: {len(employees)}
        Open Positions: {len(requisitions)}
        
        Manager Query: {query}
        
        Employee Data Sample: {json.dumps([{'name': emp.name, 'skills': emp.skills, 'status': emp.current_status} for emp in employees[:3]], default=str)}
        
        Please provide staffing recommendations and analysis.
        """
        
        try:
            response = self.ollama_client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
            
            llm_response = response['message']['content']
            print('this is the manager llm_response', llm_response)

            # Parse skill requirements from query using LLM
            skill_requirements = await self._parse_skill_requirements_ai(query)
            # matches = await self._find_employee_matches_ai(employees, skill_requirements, query)
            
            return {
                "type": "staffing_consultant_response",
                "llm_response": llm_response,
                # "structured_matches": matches,
                "search_criteria": skill_requirements,
                # "summary": self._generate_staffing_summary(matches)
            }
            
        except Exception as e:
            logger.error(f"Error in staffing consultant: {str(e)}")
            return await self._fallback_staffing_processing(query, context)

    async def _parse_skill_requirements_ai(self, query: str) -> List[Dict]:
        """Use LLM to parse skill requirements from natural language"""
        
        system_prompt = """Extract skill requirements from the query and return as structured JSON.
        Format: [{"skill_name": "Java", "min_experience": 5, "required_level": "ADVANCED", "priority": "HIGH/MEDIUM/LOW"}]
        """
        
        try:
            response = self.ollama_client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                format="json"
            )
            print('skill parsing resonse', response['message']['content'])
            return json.loads(response['message']['content'])
            
        except Exception as e:
            logger.error(f"Error parsing skills with AI: {str(e)}")
            return self._parse_skill_requirements_fallback(query)

    async def _find_employee_matches_ai(self, employees: List[Employee], requirements: List[Dict], original_query: str) -> List[Dict]:
        """Use LLM to find and rank employee matches"""
        
        system_prompt = """Analyze employees against requirements and provide intelligent matching.
        Consider: skill proficiency, experience, availability, performance, and contextual factors.
        """
        
        employee_data = []
        for emp in employees:
            if emp.current_status in ["BENCH", "TRANSITIONING", "NOTICE_PERIOD"]:
                employee_data.append({
                    "name": emp.name,
                    "skills": emp.skills,
                    "status": emp.current_status,
                    "performance": emp.performance_rating,
                    "location": emp.location
                })
        
        user_prompt = f"""
        Requirements: {json.dumps(requirements)}
        Available Employees: {json.dumps(employee_data)}
        Original Query Context: {original_query}
        
        Provide ranked matches with reasoning scores.
        """
        
        try:
            response = self.ollama_client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                format="json"
            )
            
            ai_matches = json.loads(response['message']['content'])
            print('ai_matches', ai_matches)
            
            # Enhance with calculated scores
            enhanced_matches = []
            for match in ai_matches.get("matches", []):
                emp = next((e for e in employees if e.name == match["employee_name"]), None)
                if emp:
                    enhanced_match = {
                        **match,
                        # "calculated_score": self._calculate_employee_match_score(emp, requirements),
                        "availability": self._check_availability(emp, None)
                    }
                    enhanced_matches.append(enhanced_match)
            
            return enhanced_matches
            
        except Exception as e:
            logger.error(f"Error in AI employee matching: {str(e)}")
            return await self._fallback_employee_matching(employees, requirements)

    async def _find_enhanced_matches(self, employee: Employee, requisitions: List[Requisition]) -> List[Dict]:
        """Use LLM to provide enhanced matching with reasoning"""
        
        system_prompt = """Analyze position matches for an employee considering:
        - Skill alignment and gaps
        - Career growth potential
        - Cultural and location factors
        - Timing and availability
        
        Provide nuanced matching scores with explanations.
        """
        
        user_prompt = f"""
        Employee: {employee.name}
        Skills: {json.dumps(employee.skills)}
        Status: {employee.current_status}
        Location: {employee.location}
        
        Positions: {json.dumps([asdict(req) for req in requisitions], default=str)}
        
        Provide detailed match analysis.
        """
        
        try:
            response = self.ollama_client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                format="json"
            )
            
            return json.loads(response['message']['content'])
            
        except Exception as e:
            logger.error(f"Error in enhanced matching: {str(e)}")
            return self._calculate_employee_requisition_match(employee, requisitions)

    def _generate_ai_recommendations(self, employee: Employee, requisitions: List[Requisition]) -> List[Dict]:
        """Generate AI-powered career recommendations"""
        
        system_prompt = """Based on employee profile and market opportunities, provide career development recommendations.
        Consider: skill gaps, emerging technologies, career progression paths, market trends.
        """
        
        user_prompt = f"""
        Employee Profile:
        - Skills: {json.dumps(employee.skills)}
        - Experience Level: Based on {max([s['experience_years'] for s in employee.skills])} years
        - Current Status: {employee.current_status}
        - Location: {employee.location}
        
        Market Opportunities: {len(requisitions)} open positions
        
        Provide specific, actionable recommendations.
        """
        
        try:
            response = self.ollama_client.chat(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                format="json"
            )

            print('genai recommendations', response['message']['content'])
            
            return json.loads(response['message']['content'])
            
        except Exception as e:
            logger.error(f"Error generating AI recommendations: {str(e)}")
            return self._generate_skill_recommendations(employee, [])

    def _extract_action_items(self, llm_response: str) -> List[str]:
        """Extract action items from LLM response"""
        # Simple extraction - can be enhanced with more sophisticated NLP
        action_phrases = ["should", "recommend", "suggest", "consider", "next step", "action"]
        sentences = llm_response.split('.')
        
        action_items = []
        for sentence in sentences:
            if any(phrase in sentence.lower() for phrase in action_phrases):
                action_items.append(sentence.strip())
                
        return action_items[:5]  # Return top 5 action items

    # Fallback methods (maintain original functionality as backup)
    async def _fallback_employee_processing(self, query: str, context: Dict) -> Dict:
        """Fallback employee processing"""
        employee = context.get("employee")
        if not employee:
            return {"error": "Employee not found"}
        
        if "open positions" in query.lower() or "find jobs" in query.lower():
            return await self.find_positions_for_employee(employee)
        else:
            return {
                "response": "I can help you find positions matching your skills. Please try queries like 'Find open positions' or 'Check positions for Java skills'",
                "employee": employee.name
            }

    async def _fallback_staffing_processing(self, query: str, context: Dict) -> Dict:
        """Fallback staffing processing"""
        return await self.find_employees_by_skills(query)

    async def _fallback_employee_matching(self, employees: List[Employee], requirements: List[Dict]) -> List[Dict]:
        """Fallback employee matching"""
        matches = []
        for employee in employees:
            if employee.current_status in ["BENCH", "TRANSITIONING", "NOTICE_PERIOD"]:
                match_result = self._calculate_employee_skill_match(employee, requirements)
                if match_result["total_score"] > 0:
                    matches.append(match_result)
        
        matches.sort(key=lambda x: x["total_score"], reverse=True)
        return matches

    # Maintain original calculation methods for fallback
    def _calculate_employee_skill_match(self, employee: Employee, requirements: List[Dict]) -> Dict:
        """Original skill matching logic (unchanged)"""
        # ... (keep original implementation)
        pass

    def _calculate_employee_requisition_match(self, employee: Employee, requisitions: List[Requisition]) -> List[Dict]:
        """Original requisition matching logic (unchanged)"""
        # ... (keep original implementation)
        pass

    def _calculate_skill_match_score(self, emp_skill: Dict, req_skill: Dict) -> float:
        """Original score calculation (unchanged)"""
        # ... (keep original implementation)
        pass

    def _check_availability(self, employee: Employee, requisition: Requisition) -> Dict:
        """Original availability check (unchanged)"""
        # ... (keep original implementation)
        pass

    def _generate_skill_recommendations(self, employee: Employee, matches: List[Dict]) -> List[Dict]:
        """Original recommendations (unchanged)"""
        # ... (keep original implementation)
        pass

    def _generate_staffing_summary(self, matches: List[Dict]) -> Dict:
        """Original summary generation (unchanged)"""
        # ... (keep original implementation)
        pass
