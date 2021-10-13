from tika import parser
import os
import sys


def has_grade(line):
    line_words = line.split(" ")
    if len(line_words) < 3:
        return False

    if line_words[-2].replace(".", "", 1).isnumeric() and \
        line_words[-3].replace(".", "", 1).isnumeric():
        return True
    else:
        return False

def is_multiline(lines, idx):
    if len(lines)-1 < idx+2:
        return False

    if not has_grade(lines[idx]) and \
        len(lines[idx+2].split(" ")) == 3 and has_grade(lines[idx+2]):
        return True
    else:
        return False

def gpa_lookup(x):
    if   (90 <= x <= 100): return 4.0
    elif (85 <= x <= 89): return 3.9
    elif (80 <= x <= 84): return 3.7
    elif (77 <= x <= 79): return 3.3
    elif (73 <= x <= 76): return 3.0
    elif (70 <= x <= 72): return 2.7
    elif (67 <= x <= 69): return 2.3
    elif (63 <= x <= 66): return 2.0
    elif (60 <= x <= 62): return 1.7
    elif (57 <= x <= 59): return 1.3
    elif (53 <= x <= 56): return 1.0
    elif (50 <= x <= 52): return 0.7
    elif (x <= 49): return 0.0
    else: print("Invalid mark")


filepath = sys.argv[1]
if not os.path.exists(filepath):
    print("Provided path does not exist\n")
    exit(1)

raw = parser.from_file(filepath)
lines = [x.strip() for x in raw['content'].split('\n') if x.strip() != ""]

if lines[0] != "University of Waterloo" or \
    lines[5] != "Undergraduate Unofficial Transcript":
    print("Please use your UWaterloo Undergraduate Unofficial Transcript\n")
    exit(1)


# preprocessing
idx = 0
while lines[idx+1] != "End of Undergraduate Unofficial Transcript":
    idx += 1

    if is_multiline(lines, idx):
        lines[idx] = f"{lines[idx]} {lines[idx+1]} {lines[idx+2]}"
        del lines[idx+1]
        del lines[idx+1]


avg_total = 0
gpa_total = 0
weight_total = 0

curr_term = ""
transcript_avg = 0.0

for i in range(0, len(lines)):
    if lines[i].__contains__("Level:"):
        curr_term = lines[i].split()[1]

    if lines[i].__contains__("Cumulative GPA"):
        transcript_avg = float(lines[i].split()[2])

    if lines[i] == "Course Description Attempted Earned Grade":

        # skip in progress terms
        if not has_grade(lines[i+1]):
            break

        term_avg = 0
        term_gpa = 0
        term_weight = 0

        while lines[i+1] != "In GPA Earned":
            i += 1

            # ignore CR, NCR, COVID-19 note, etc.
            line = lines[i].split(" ")
            if not line[-1].isnumeric():
                continue

            grade = int(line[-1])
            weight = float(line[-2])

            term_avg += grade * weight
            term_gpa += gpa_lookup(grade) * weight
            term_weight += weight

        if term_weight != 0:

            avg_total += term_avg
            gpa_total += term_gpa
            weight_total += term_weight

            print(f"\n{curr_term} avg: {term_avg / term_weight}")
            print(f"{curr_term} gpa: {term_gpa / term_weight}")

print('\n--------------------------------------------\n')

cavg = avg_total / weight_total
cgpa = gpa_total / weight_total

print(f"cavg: {cavg}")
print(f"cgpa: {cgpa}\n")

if (round(cavg, 2) != transcript_avg):
    print(f"Sorry, something may have gone wrong. Calculated avg ({round(cavg, 2)}) doesn't match transcript avg ({transcript_avg})")
