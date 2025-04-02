package uk.ac.rhul.cs2800.model;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Test class for Module.
 */
public class ModuleTest {

  /**
   * Tests the attributes of the Module class.
   */
  @Test
  public void testModuleAttributes() {
    Module module = new Module("CS101", "Intro to Programming", true);

    // Tests code and name attributes.
    assertEquals("CS101", module.getCode());
    assertEquals("Intro to Programming", module.getName());

    // Tests mandatory status.
    assertTrue(module.isMandatory());
  }
}
