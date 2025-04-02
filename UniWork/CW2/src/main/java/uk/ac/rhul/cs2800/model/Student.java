package uk.ac.rhul.cs2800.model;

import jakarta.persistence.CascadeType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.OneToMany;
import java.util.ArrayList;
import java.util.List;

/**
 * Represents a student with first and last name, ID, username, and email.
 */
@Entity
public class Student {

  @Id
  @GeneratedValue(strategy = GenerationType.IDENTITY)
  private Long id;

  /**
   * The students first name.
   */
  private String firstName;

  /**
   * The students last name.
   */
  private String lastName;

  /**
   * The student's username.
   */
  @Column(unique = true, nullable = false)
  private String username;

  /**
   * The students email address.
   */
  @Column(unique = true, nullable = false)
  private String email;

  /**
   * The list of registrations linking this student to modules.
   */
  @OneToMany(mappedBy = "student", cascade = CascadeType.ALL, orphanRemoval = true)
  private List<Registration> registeredModules = new ArrayList<>();

  /**
   * The list of grades the student has received.
   */
  @OneToMany(mappedBy = "student", cascade = CascadeType.ALL, orphanRemoval = true)
  private List<Grade> grades = new ArrayList<>();

  /**
   * Default constructor for JPA.
   */
  public Student() {}

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
   * Registers the student to a module by creating a new registration.
   *
   * @param module the module to register the student for.
   */
  public void registerModule(Module module) {
    Registration registration = new Registration(this, module);
    registeredModules.add(registration);
  }

  /**
   * Checks if the student is registered for a given module.
   *
   * @param module the module to check.
   * @return true if registered, false otherwise.
   */
  private boolean isRegisteredForModule(Module module) {
    for (Registration reg : registeredModules) {
      if (reg.getModule().equals(module)) {
        return true;
      }
    }
    return false;
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
   * @throws NoRegistrationException if the student is not registered in the module.
   */
  public void addGrade(Grade grade) throws NoRegistrationException {
    Module module = grade.getModule();
    if (!isRegisteredForModule(module)) {
      throw new NoRegistrationException("Student is not registered in the module: "
          + module.getName());
    }
    grades.add(grade);
  }

  /**
   * Retrieves the grade for a module.
   *
   * @param module the module to retrieve the grade for.
   * @return the grade for the specified module.
   * @throws NoGradeAvailableException if no grade is available for the module.
   * @throws NoRegistrationException   if the student is not registered in the module.
   */
  public Grade getGrade(Module module) throws NoGradeAvailableException, NoRegistrationException {
    if (!isRegisteredForModule(module)) {
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
