from haystack import Document
from haystack.components.builders import PromptBuilder

documents = [
Document(content="Statistical tests, probability distributions, and algorithms", 
         meta={
            'name': "Intermediate Statistics",
            'code': "MA331",
            'link': "www.exampleSchool.com/MA331"             
         }),
Document(content="Introduction to data structures, algorithms, and computational complexity", 
         meta={
            'name': "Data Structures and Algorithms",
            'code': "CS210",
            'link': "www.exampleSchool.com/CS210"
         }),
Document(content="Principles of microeconomic theory, market structures, and consumer behavior", 
         meta={
            'name': "Microeconomics",
            'code': "EC201",
            'link': "www.exampleSchool.com/EC201"
         }),
Document(content="Study of classical mechanics, kinematics, and dynamics", 
         meta={
            'name': "Physics I: Mechanics",
            'code': "PH101",
            'link': "www.exampleSchool.com/PH101"
         }),
Document(content="Organic reactions, stereochemistry, and molecular structures", 
         meta={
            'name': "Organic Chemistry",
            'code': "CH221",
            'link': "www.exampleSchool.com/CH221"
         }),
Document(content="Advanced calculus covering multivariable functions and vector calculus", 
         meta={
            'name': "Multivariable Calculus",
            'code': "MA241",
            'link': "www.exampleSchool.com/MA241"
         }),
Document(content="Historical analysis of global civilizations from 1500 to present", 
         meta={
            'name': "World History: Modern Era",
            'code': "HI202",
            'link': "www.exampleSchool.com/HI202"
         }),
Document(content="Concepts of object-oriented programming using Python and Java", 
         meta={
            'name': "Object-Oriented Programming",
            'code': "CS220",
            'link': "www.exampleSchool.com/CS220"
         }),
Document(content="Introduction to human anatomy, physiology, and biological systems", 
         meta={
            'name': "Human Biology",
            'code': "BI110",
            'link': "www.exampleSchool.com/BI110"
         }),
Document(content="The study of differential equations and their applications in real-world systems", 
         meta={
            'name': "Differential Equations",
            'code': "MA351",
            'link': "www.exampleSchool.com/MA351"
         })
]

year = 2024
template = f"""\
Given the following information about courses from the fall semester of {year} to the spring semester of {year+1} at Stevens Institute of Technology, provide a descriptive answer to the question. The courses are ordered from most relevant to least relevant. Please include the course code and the link to the course catalog page in your answer.

Courses: 
\u007b% for doc in documents %\u007d
    \u007b\u007b loop.index \u007d\u007d. \u007b\u007b doc.meta['name'] \u007d\u007d
    \u007b\u007b doc.content \u007d\u007d
    Course code: \u007b\u007b doc.meta['code'] \u007d\u007d
    Link to catalog page: \u007b\u007b doc.meta['link'] \u007d\u007d
\u007b% endfor %\u007d

Question: \u007b\u007b query \u007d\u007d?\
"""

builder = PromptBuilder(template=template)

question = "What class should I take if I like chemistry"

out = builder.run(documents=documents, query=question)

print(out['prompt'])