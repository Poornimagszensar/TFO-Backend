import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, date
from dataclasses import dataclass
import asyncio

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

class TFOChatbot:
    def __init__(self):
        self.employees = self._load_mock_employees()
        self.requisitions = self._load_mock_requisitions()
        self.skill_ontology = self._load_skill_ontology()

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

    async def process_employee_query(self, employee_id: str, query: str) -> Dict:
        """Process employee queries for finding open positions"""
        employee = next((emp for emp in self.employees if emp.employee_id == employee_id), None)
        if not employee:
            return {"error": "Employee not found"}
        
        if "open positions" in query.lower() or "find jobs" in query.lower() or "opportunities" in query.lower():
            return await self.find_positions_for_employee(employee)
        
        elif "check position" in query.lower() or "specific skills" in query.lower():
            return await self.find_positions_with_specific_skills(employee, query)
        
        else:
            return {
                "response": "I can help you with:\n1. Finding open positions matching your skills\n2. Checking positions for specific skills\n3. Skill upgrade recommendations\n\nHow can I assist you?",
                "employee": employee.name,
                "status": employee.current_status
            }

    async def process_manager_query(self, user_role: str, query: str) -> Dict:
        """Process manager/TSC queries for finding employees"""
        if "find employees" in query.lower() or "search resources" in query.lower() or "java react angular" in query.lower():
            return await self.find_employees_by_skills(query)
        else:
            return {
                "response": "I can help you find employees with specific skill sets. Please specify the skills and experience levels you're looking for.",
                "user_role": user_role
            }

    async def find_positions_for_employee(self, employee: Employee) -> Dict:
        """Find open positions matching employee skills"""
        matches = []
        
        for req in self.requisitions:
            if req.status != "OPEN":
                continue
                
            match_result = self._calculate_employee_requisition_match(employee, req)
            if match_result["total_score"] > 0:  # Show all matches, even low scores
                matches.append(match_result)
        
        # Sort by match score
        matches.sort(key=lambda x: x["total_score"], reverse=True)
        
        response = {
            "employee": employee.name,
            "current_status": employee.current_status,
            "total_matches": len(matches),
            "matches": matches[:5],  # Top 5 matches
            "recommendations": self._generate_skill_recommendations(employee, matches)
        }
        
        return response

    async def find_positions_with_specific_skills(self, employee: Employee, query: str) -> Dict:
        """Find positions for specific skills mentioned in query"""
        # Extract skills from query (simplified parsing)
        query_skills = []
        skill_keywords = ["java", "react", "angular", "python", "sql", "spring", "node", "aws"]
        
        for skill in skill_keywords:
            if skill in query.lower():
                query_skills.append(skill)
        
        if not query_skills:
            return {
                "response": "Please specify which skills you want to check positions for. For example: 'Check positions for Java and React skills'",
                "employee": employee.name
            }
        
        filtered_requisitions = []
        for req in self.requisitions:
            if req.status != "OPEN":
                continue
                
            req_skills = [skill["skill_name"].lower() for skill in req.required_skills]
            if any(skill in req_skills for skill in query_skills):
                match_result = self._calculate_employee_requisition_match(employee, req)
                filtered_requisitions.append(match_result)
        
        filtered_requisitions.sort(key=lambda x: x["total_score"], reverse=True)
        
        return {
            "employee": employee.name,
            "searched_skills": query_skills,
            "matching_positions": filtered_requisitions,
            "skill_gap_analysis": self._analyze_skill_gaps_for_query(employee, query_skills)
        }

    async def find_employees_by_skills(self, query: str) -> Dict:
        """Find employees matching specific skill requirements"""
        # Parse skill requirements from query
        requirements = self._parse_skill_requirements(query)
        if not requirements:
            return {
                "error": "Please specify skill requirements. Example: 'Find employees with Java 5+ years, React 2+ years, Angular 3+ years'"
            }
        
        matches = []
        for employee in self.employees:
            # Filter by availability
            if employee.current_status not in ["BENCH", "TRANSITIONING", "NOTICE_PERIOD"]:
                continue
                
            match_result = self._calculate_employee_skill_match(employee, requirements)
            if match_result["total_score"] > 0:
                matches.append(match_result)
        
        matches.sort(key=lambda x: x["total_score"], reverse=True)
        
        return {
            "search_criteria": requirements,
            "total_employees_found": len(matches),
            "matches": matches,
            "summary": self._generate_search_summary(matches, requirements)
        }

    def _parse_skill_requirements(self, query: str) -> List[Dict]:
        """Parse skill requirements from natural language query"""
        requirements = []
        
        # Simplified parsing - in real implementation, use NLP
        if "java" in query.lower():
            requirements.append({"skill_name": "Java", "min_experience": 5, "required_level": "ADVANCED"})
        if "react" in query.lower() and "2" in query:
            requirements.append({"skill_name": "React", "min_experience": 2, "required_level": "INTERMEDIATE"})
        if "angular" in query.lower() and "3" in query:
            requirements.append({"skill_name": "Angular", "min_experience": 3, "required_level": "ADVANCED"})
        if "sql" in query.lower():
            requirements.append({"skill_name": "SQL", "min_experience": 1, "required_level": "INTERMEDIATE"})
        
        return requirements

    def _calculate_employee_requisition_match(self, employee: Employee, requisition: Requisition) -> Dict:
        """Calculate match score between employee and requisition"""
        total_score = 0
        skill_matches = []
        missing_skills = []
        
        for req_skill in requisition.required_skills:
            emp_skill = next((s for s in employee.skills if s["skill_name"].lower() == req_skill["skill_name"].lower()), None)
            
            if emp_skill:
                skill_score = self._calculate_skill_match_score(emp_skill, req_skill)
                skill_matches.append({
                    "skill": req_skill["skill_name"],
                    "required_experience": req_skill["min_experience"],
                    "employee_experience": emp_skill["experience_years"],
                    "match_score": skill_score,
                    "status": "MATCHED"
                })
                total_score += skill_score * (2 if req_skill["is_mandatory"] else 1)
            else:
                missing_skills.append({
                    "skill": req_skill["skill_name"],
                    "required_experience": req_skill["min_experience"],
                    "required_level": req_skill["required_level"],
                    "is_mandatory": req_skill["is_mandatory"]
                })
        
        # Normalize score
        max_score = sum(2 for skill in requisition.required_skills if skill["is_mandatory"]) + \
                   sum(1 for skill in requisition.required_skills if not skill["is_mandatory"])
        normalized_score = (total_score / max_score * 100) if max_score > 0 else 0
        
        return {
            "requisition_id": requisition.requisition_id,
            "project_name": requisition.project_name,
            "role_title": requisition.role_title,
            "location": requisition.location,
            "start_date": requisition.start_date.isoformat(),
            "total_score": round(normalized_score, 2),
            "skill_matches": skill_matches,
            "missing_skills": missing_skills,
            "availability_status": self._check_availability(employee, requisition)
        }

    def _calculate_employee_skill_match(self, employee: Employee, requirements: List[Dict]) -> Dict:
        """Calculate how well employee matches skill requirements"""
        total_score = 0
        matched_skills = []
        missing_skills = []
        
        for req in requirements:
            emp_skill = next((s for s in employee.skills if s["skill_name"].lower() == req["skill_name"].lower()), None)
            
            if emp_skill:
                skill_score = self._calculate_skill_match_score(emp_skill, req)
                matched_skills.append({
                    "skill": req["skill_name"],
                    "required_experience": req["min_experience"],
                    "employee_experience": emp_skill["experience_years"],
                    "employee_level": emp_skill["proficiency_level"],
                    "match_score": skill_score
                })
                total_score += skill_score
            else:
                missing_skills.append({
                    "skill": req["skill_name"],
                    "required_experience": req["min_experience"],
                    "required_level": req["required_level"]
                })
        
        normalized_score = (total_score / len(requirements)) * 100 if requirements else 0
        
        return {
            "employee_id": employee.employee_id,
            "employee_name": employee.name,
            "current_status": employee.current_status,
            "location": employee.location,
            "performance_rating": employee.performance_rating,
            "total_score": round(normalized_score, 2),
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "bench_days": self._calculate_bench_days(employee) if employee.bench_start_date else 0
        }

    def _calculate_skill_match_score(self, emp_skill: Dict, req_skill: Dict) -> float:
        """Calculate individual skill match score"""
        score = 0
        
        # Experience match (0-70 points)
        exp_ratio = min(emp_skill["experience_years"] / req_skill["min_experience"], 2.0)  # Cap at 2x required
        score += min(exp_ratio * 35, 70)
        
        # Proficiency level match (0-30 points)
        level_scores = {"BEGINNER": 10, "INTERMEDIATE": 20, "ADVANCED": 30, "EXPERT": 30}
        emp_level_score = level_scores.get(emp_skill["proficiency_level"], 0)
        req_level_score = level_scores.get(req_skill["required_level"], 15)
        score += min(emp_level_score, req_level_score)
        
        return score / 100.0  # Normalize to 0-1

    def _check_availability(self, employee: Employee, requisition: Requisition) -> Dict:
        """Check employee availability for requisition"""
        if employee.current_status == "BENCH":
            return {"status": "IMMEDIATELY_AVAILABLE", "details": "On bench"}
        elif employee.current_status == "NOTICE_PERIOD":
            return {"status": "AVAILABLE_SOON", "details": f"Notice period ends {employee.project_end_date}"}
        elif employee.current_status == "TRANSITIONING":
            days_until_available = (employee.project_end_date - date.today()).days
            return {"status": "AVAILABLE_SOON", "details": f"Available in {days_until_available} days"}
        else:
            return {"status": "NOT_AVAILABLE", "details": "Currently on active project"}

    def _calculate_bench_days(self, employee: Employee) -> int:
        """Calculate number of days on bench"""
        if employee.bench_start_date:
            return (date.today() - employee.bench_start_date).days
        return 0

    def _generate_skill_recommendations(self, employee: Employee, matches: List[Dict]) -> List[Dict]:
        """Generate skill upgrade recommendations based on missing skills in high-scoring matches"""
        recommendations = []
        
        for match in matches[:3]:  # Top 3 matches
            for missing_skill in match.get("missing_skills", []):
                if missing_skill["is_mandatory"]:
                    recommendations.append({
                        "skill": missing_skill["skill"],
                        "required_experience": missing_skill["required_experience"],
                        "required_level": missing_skill["required_level"],
                        "priority": "HIGH",
                        "suggested_training": self._get_training_suggestions(missing_skill["skill"])
                    })
        
        # Remove duplicates
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            key = rec["skill"]
            if key not in seen:
                seen.add(key)
                unique_recommendations.append(rec)
        
        return unique_recommendations

    def _analyze_skill_gaps_for_query(self, employee: Employee, query_skills: List[str]) -> Dict:
        """Analyze skill gaps for specific query skills"""
        gaps = []
        for skill in query_skills:
            emp_skill = next((s for s in employee.skills if s["skill_name"].lower() == skill), None)
            if not emp_skill:
                gaps.append({
                    "skill": skill,
                    "status": "MISSING",
                    "recommendation": f"Consider learning {skill} to expand opportunities",
                    "priority": "MEDIUM"
                })
        
        return {"skill_gaps": gaps, "total_gaps": len(gaps)}

    def _generate_search_summary(self, matches: List[Dict], requirements: List[Dict]) -> Dict:
        """Generate summary of employee search results"""
        total_employees = len(matches)
        high_matches = len([m for m in matches if m["total_score"] >= 80])
        medium_matches = len([m for m in matches if 50 <= m["total_score"] < 80])
        low_matches = len([m for m in matches if m["total_score"] < 50])
        
        return {
            "total_employees": total_employees,
            "high_matches": high_matches,
            "medium_matches": medium_matches,
            "low_matches": low_matches,
            "recommendation": self._get_staffing_recommendation(matches, requirements)
        }

    def _get_staffing_recommendation(self, matches: List[Dict], requirements: List[Dict]) -> str:
        """Provide staffing recommendation based on match results"""
        if not matches:
            return "No suitable internal candidates found. Consider external hiring."
        
        high_matches = [m for m in matches if m["total_score"] >= 80]
        if high_matches:
            return f"Found {len(high_matches)} excellent matches. Recommend proceeding with internal hiring."
        
        medium_matches = [m for m in matches if 50 <= m["total_score"] < 80]
        if medium_matches:
            return f"Found {len(medium_matches)} potential matches with some skill gaps. Consider training or external backup."
        
        return "Limited internal matches. Strongly recommend external hiring with internal backup plan."

    def _get_training_suggestions(self, skill: str) -> List[str]:
        """Get training suggestions for skill upgrades"""
        training_map = {
            "Java": ["Java Certification", "Spring Boot Fundamentals", "Microservices Architecture"],
            "React": ["React Advanced Patterns", "State Management with Redux", "React Testing"],
            "Angular": ["Angular Framework Deep Dive", "RxJS Fundamentals", "Angular Performance"],
            "Python": ["Python for Web Development", "Django REST Framework", "Python Design Patterns"],
            "SQL": ["Advanced SQL Queries", "Database Optimization", "SQL Performance Tuning"]
        }
        return training_map.get(skill, [f"{skill} Fundamentals", f"Advanced {skill} Concepts"])

