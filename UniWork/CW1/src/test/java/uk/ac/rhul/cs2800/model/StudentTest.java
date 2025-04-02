
package uk.ac.rhul.cs2800.model;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Test class for Student.
 */
public class StudentTest {

  /**
   * Tests the attributes of a Student: ID, first name, last name, username, and email.
   */
  @Test
  public void testIdFirstNameLastNameUsernameEmail() {
    Student student = new Student(1L, "Krishna", "Dattani", "ZMAC267", 
        "ZMAC267@live.rhul.ac.uk");
    assertEquals(1L, student.getId());
    assertEquals("Krishna", student.getFirstName());
    assertEquals("Dattani", student.getLastName());
    assertEquals("ZMAC267", student.getUsername());
    assertEquals("ZMAC267@live.rhul.ac.uk", student.getEmail());
  }

  /**
   * Tests registering a module and adding a grade to the module.
   *
   * @throws NoRegistrationException if the student is not registered in the module.
   */
  @Test
  public void testRegisterModule() throws NoRegistrationException {
    Student student = new Student(1L, "Krishna", "Dattani", "ZMAC267", 
        "ZMAC267@live.rhul.ac.uk");
    Module module = new Module("CS101", "Intro to Programming", true);

    // Register the module.
    student.registerModule(module);

    // Verify registration by attempting to add a grade.
    Grade grade = new Grade(85, module);
    assertDoesNotThrow(() -> student.addGrade(grade));
  }

  /**
   * Tests computing the average when no grades are available.
   */
  @Test
  public void testComputeAverageWithNoGrades() {
    Student student = new Student(1L, "Krishna", "Dattani", "ZMAC267", 
        "ZMAC267@live.rhul.ac.uk");
    assertEquals(0, student.computeAverage(), 
        "Average should be 0 when there are no grades.");
  }

  /**
   * Tests computing the average with one grade.
   *
   * @throws NoRegistrationException if the student is not registered in the module.
   */
  @Test
  public void testComputeAverageWithOneGrade() throws NoRegistrationException {
    Student student = new Student(1L, "Krishna", "Dattani", "ZMAC267", 
        "ZMAC267@live.rhul.ac.uk");
    Module module = new Module("CS101", "Intro to Programming", true);
    student.registerModule(module);
    student.addGrade(new Grade(80, module));
    assertEquals(80, student.computeAverage(), 
        "Average should be the grade itself when there is only one grade.");
  }

  /**
   * Tests computing the average with multiple grades.
   *
   * @throws NoRegistrationException if the student is not registered in the module.
   */
  @Test
  public void testComputeAverageWithMultipleGrades() throws NoRegistrationException {
    Student student = new Student(1L, "Krishna", "Dattani", "ZMAC267", 
        "ZMAC267@live.rhul.ac.uk");
    Module module1 = new Module("CS101", "Intro to Programming", true);
    Module module2 = new Module("CS102", "Data Structures", true);
    student.registerModule(module1);
    student.registerModule(module2);
    student.addGrade(new Grade(80, module1));
    student.addGrade(new Grade(90, module2));
    assertEquals(85, student.computeAverage(), 
        "Average should be the mean of all grades.");
  }

  /**
   * Tests adding a grade for a registered module.
   *
   * @throws NoRegistrationException if the student is not registered in the module.
   * @throws NoGradeAvailableException if no grade is available for the module.
   */
  @Test
  public void testAddGradeForRegisteredModule() 
      throws NoRegistrationException, NoGradeAvailableException {
    Student student = new Student(1L, "Krishna", "Dattani", "ZMAC267", 
        "ZMAC267@live.rhul.ac.uk");
    Module module = new Module("CS101", "Intro to Programming", true);
    Grade grade = new Grade(85, module);

    student.registerModule(module);
    student.addGrade(grade);
    assertEquals(grade, student.getGrade(module));
  }

  /**
   * Tests adding a grade for an unregistered module.
   */
  @Test
  public void testAddGradeForUnregisteredModule() {
    Student student = new Student(1L, "Krishna", "Dattani", "ZMAC267", 
        "ZMAC267@live.rhul.ac.uk");
    Module module = new Module("CS101", "Intro to Programming", true);
    Grade grade = new Grade(85, module);

    Exception exception = assertThrows(NoRegistrationException.class, 
        () -> student.addGrade(grade));
    assertEquals("Student is not registered in the module: Intro to Programming", 
        exception.getMessage());
  }

  /**
   * Tests retrieving a grade for a registered module with an assigned grade.
   *
   * @throws NoGradeAvailableException if no grade is available for the module.
   * @throws NoRegistrationException   if the student is not registered in the module.
   */
  @Test
  public void testGetGradeForRegisteredModuleWithGrade() 
      throws NoGradeAvailableException, NoRegistrationException {
    Student student = new Student(1L, "Krishna", "Dattani", "ZMAC267", 
        "ZMAC267@live.rhul.ac.uk");
    Module module = new Module("CS101", "Intro to Programming", true);
    Grade grade = new Grade(85, module);

    student.registerModule(module);
    student.addGrade(grade);
    assertEquals(85, student.getGrade(module).getScore());
  }

  /**
   * Tests retrieving a grade for a registered module without an assigned grade.
   */
  @Test
  public void testGetGradeForRegisteredModuleWithoutGrade() {
    Student student = new Student(1L, "Krishna", "Dattani", "ZMAC267", 
        "ZMAC267@live.rhul.ac.uk");
    Module module = new Module("CS101", "Intro to Programming", true);
    student.registerModule(module);

    Exception exception = assertThrows(NoGradeAvailableException.class, 
        () -> student.getGrade(module));
    assertEquals("No grade available for module: Intro to Programming", 
        exception.getMessage());
  }

  /**
   * Tests retrieving a grade for an unregistered module.
   */
  @Test
  public void testGetGradeForUnregisteredModule() {
    Student student = new Student(1L, "Krishna", "Dattani", "ZMAC267", 
        "ZMAC267@live.rhul.ac.uk");
    Module module = new Module("CS101", "Intro to Programming", true);

    Exception exception = assertThrows(NoRegistrationException.class, 
        () -> student.getGrade(module));
    assertEquals("Student is not registered in the module: Intro to Programming", 
        exception.getMessage());
  }
}
