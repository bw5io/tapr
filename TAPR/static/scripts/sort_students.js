let SurnameF = document.getElementById("SurnameF");
let Surname = document.getElementById("Surname");
let FirstNameF = document.getElementById("FirstNameF");
let FirstName = document.getElementById("FirstName");
let NativeSpeakerF = document.getElementById("NativeSpeakerF");
let NativeSpeaker = document.getElementById("NativeSpeaker");
let CodingExperienceF = document.getElementById("CodingExperienceF");
let CodingExperience = document.getElementById("CodingExperience");
let PreviousDegreeF = document.getElementById("PreviousDegreeF");
let PreviousDegree = document.getElementById("PreviousDegree");

WholeSection.innerHTML = "";
WholeSection.append(Surname);

//default: display surname
SurnameF.addEventListener("click", function(){
    WholeSection.innerHTML = "";
    WholeSection.append(Surname);
});
//display First Name
FirstNameF.addEventListener("click", function(){
    WholeSection.innerHTML = "";
    WholeSection.append(FirstName);
});
//display Native Speaker
NativeSpeakerF.addEventListener("click", function(){
    WholeSection.innerHTML = "";
    WholeSection.append(NativeSpeaker);
});
//display Coding experience
CodingExperienceF.addEventListener("click", function(){
    WholeSection.innerHTML = "";
    WholeSection.append(CodingExperience);
});
//display Previous Degree
PreviousDegreeF.addEventListener("click", function(){
    WholeSection.innerHTML = "";
    WholeSection.append(PreviousDegree);
});
