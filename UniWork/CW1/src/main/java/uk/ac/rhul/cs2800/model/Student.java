package uk.ac.rhul.cs2800.model;

import java.util.ArrayList;
import java.util.List;

/**
 * Represents a student with a first and last name.
 */
public class Student {
  private String firstName;
  private String lastName;
  private Long id;
  private String username;
  private String email;
  private List<Module> registeredModules;
  private List<Grade> grades;

  /**
   * Creates a new student with the specified details.
   *
   * @param id        the student's ID.
   * @param firstName the student's first name.
   * @param lastName  the student's last name.
   * @param username  the student's username.
   * @param email     the student's email address.
   */
  public Student(Long id, String firstName, String lastName, String username, String email) {
    this.id = id;
    this.firstName = firstName;
    this.lastName = lastName;
    this.username = username;
    this.email = email;
    this.registeredModules = new ArrayList<>();
    this.grades = new ArrayList<>();
  }

  /**
   * Returns the student's first name.
   *
   * @return the first name.
   */
  public String getFirstName() {
    return firstName;
  }

  /**
   * Returns the student's last name.
   *
   * @return the last name.
   */
  public String getLastName() {
    return lastName;
  }

  /**
   * Returns the student's ID.
   *
   * @return the ID.
   */
  public Long getId() {
    return id;
  }

  /**
   * Returns the student's username.
   *
   * @return the username.
   */
  public String getUsername() {
    return username;
  }

  /**
   * Returns the student's email address.
   *
   * @return the email.
   */
  public String getEmail() {
    return email;
  }

  /**
   * Registers a student to a module.
   *
   * @param module the module to register the student for.
   */
  public void registerModule(Module module) {
    registeredModules.add(module);
  }

  /**
   * Computes the average of the student's grades.
   *
   * @return the average score of all grades or 0 if no grades are available.
   */
  public float computeAverage() {
    if (grades.isEmpty()) {
      return 0;
    }

    int total = 0;
    for (Grade grade : grades) {
      total += grade.getScore();
    }
    return (float) total / grades.size();
  }

  /**
   * Adds a grade for a module if the student is registered.
   *
   * @param grade the grade to add.
   * 
   * @throws NoRegistrationException if the student is not registered in the module.
   */
  public void addGrade(Grade grade) throws NoRegistrationException {
    if (!registeredModules.contains(grade.getModule())) {
      throw new NoRegistrationException("Student is not registered in the module: "
          + grade.getModule().getName());
    }
    grades.add(grade);
  }

  /**
   * Retrieves the grade for a module.
   *
   * @param module the module to retrieve the grade for.
   * 
   * @return the grade for the specified module.
   * 
   * @throws NoGradeAvailableException if no grade is available for the module.
   * @throws NoRegistrationException   if the student is not registered in the module.
   */
  public Grade getGrade(Module module) throws NoGradeAvailableException, NoRegistrationException {
    if (!registeredModules.contains(module)) {
      throw new NoRegistrationException("Student is not registered in the module: "
          + module.getName());
    }

    for (Grade grade : grades) {
      if (grade.getModule().equals(module)) {
        return grade;
      }
    }

    throw new NoGradeAvailableException("No grade available for module: " + module.getName());
  }
}
