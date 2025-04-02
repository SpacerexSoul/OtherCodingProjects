package uk.ac.rhul.cs2800.model;

/**
 * Represents a module with a unique code, name, and mandatory status.
 */
public class Module {
  private String code;
  private String name;
  private boolean mandatory;

  /**
   * Constructs a new module.
   *
   * @param code      the module code.
   * @param name      the module name.
   * @param mandatory whether the module is mandatory.
   */
  public Module(String code, String name, boolean mandatory) {
    this.code = code;
    this.name = name;
    this.mandatory = mandatory;
  }

  /**
   * Returns the module code.
   *
   * @return the code.
   */
  public String getCode() {
    return code;
  }

  /**
   * Returns the module name.
   *
   * @return the name.
   */
  public String getName() {
    return name;
  }

  /**
   * Returns whether the module is mandatory.
   *
   * @return true if the module is mandatory, false otherwise.
   */
  public boolean isMandatory() {
    return mandatory;
  }
}
