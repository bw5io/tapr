# Code to Flash all Error Messages
# taken from Stack Overflow post by i_4_got 27-11-2012
# accessed 1-2-2021
# https://stackoverflow.com/questions/13585663/flask-wtfform-flash-does-not-display-errors

from flask import flash
import io, csv
from flask import make_response


def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            flash( (error), 'error')

# end of referenced code.
def render_csv (header, data, filename="export.csv"):
    dest = io.StringIO()
    writer = csv.writer(dest)
    writer.writerow(header.split(","))
    for row in data:
        writer.writerow(row.__repr__().split(","))
    output = make_response(dest.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename="+filename
    output.headers["Content-type"] = "text/csv"
    return output

#-------------------------------------------TEAM ALLOCATION------------------------------------------------------------
def hasCodingExperience(team):
    #Function to check if team already has a member with coding experience
    for team_student in team.team_members:
        if team_student.coding_experience:
            return True
    return False

def hasPriorDegree(team, degree):
    #Function to check if team already has a member with a specific prior degree
    for team_student in team.team_members:
        if team_student.previous_degree == degree:
            return True
    return False

def notAllocated(student):
    #Function to check if student allocated to a team
    if student.team_id == None:
        return True
    else:
        return False
    
def getTeamSize(students, team_id):
    #Function to get the current size of the team
    count = 0
    for student in students:
        if student.team_id == team_id:
            count+=1
    return count

def addNativeSpeakers(teams, students):
    #Function to allocate one native speaker to each team in teams
    for team in teams:
        for student in students:
            if student.native_speaker and notAllocated(student):
                student.team_id = team.id
                break

def addPriorProgrammers(teams, students):
    #Function to allocate one prior programmer to each team in teams
    for team in teams:
        if hasCodingExperience(team): 
            continue
        else:
            for student in students:
                if student.coding_experience and notAllocated(student):
                    student.team_id = team.id
                    break

def addPreviousDegrees(teams, students, min_team_size):
    #Function to allocate members to a team where each student has a distinct prior degree subject to their teammates
    degrees = ["BA", "BSc", "BEng", "LLB"]
    for degree in degrees:
        for team in teams:
            if getTeamSize(students, team.id) == min_team_size: 
                continue
            if hasPriorDegree(team, degree):
                continue
            for student in students:
                if student.previous_degree == degree and notAllocated(student):
                    student.team_id = team.id
                    break

def allocateStudents(teams, students, min_team_size):
    #Function to fill teams to min capacity and then add any remaining students 
    for team in teams:
        for student in students:
            if getTeamSize(students, team.id) == min_team_size:
                break
            elif notAllocated(student):
                student.team_id = team.id
    for team in teams:
        for student in students:
            if notAllocated(student):
                student.team_id = team.id
                break


#----------------------------------------------------------------------------------------------------------------------
