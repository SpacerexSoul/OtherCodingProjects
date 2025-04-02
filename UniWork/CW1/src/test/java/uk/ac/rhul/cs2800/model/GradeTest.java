package uk.ac.rhul.cs2800.model;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;

/**
 * Test class for Grade.
 */
public class GradeTest {

  /**
   * Tests the attributes of the Grade class.
   */
  @Test
  public void testGradeAttributes() {
    Module module = new Module("CS101", "Intro to Programming", true);
    Grade grade = new Grade(85, module);

    // Tests the score attribute.
    assertEquals(85, grade.getScore());

    // Tests the module association.
    assertEquals(module, grade.getModule());
  }
}
