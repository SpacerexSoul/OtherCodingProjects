package uk.ac.rhul.cs2800.config;

import static org.springframework.security.config.Customizer.withDefaults;

import java.util.Arrays;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

/**
 * Configures the security settings for the application, including CORS and CSRF handling.
 */
@Configuration
public class SecurityConfig {

  /**
   * Configures the security filter chain for the application.
   * This disables CSRF and enables CORS with default settings.
   *
   * @param http the {@link HttpSecurity} object to configure
   * @return the configured {@link SecurityFilterChain}
   * @throws Exception if an error occurs during configuration
   */
  @Bean
  public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
    http.csrf((csrf) -> csrf.disable())
        .cors(withDefaults());

    return http.build();
  }

  /**
   * Configures CORS settings for the application, allowing all origins, headers, and methods.
   *
   * @return the configured {@link CorsConfigurationSource}
   */
  @Bean
  public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOriginPatterns(Arrays.asList("*"));
    config.setAllowedHeaders(Arrays.asList("*"));
    config.setAllowedMethods(Arrays.asList("*"));
    config.setAllowCredentials(false);

    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/**", config);

    return source;
  }
}
