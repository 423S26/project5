module.exports = [
  {
    files: ["**/*.js"],
    languageOptions: {
      ecmaVersion: 2021,
      globals: {
        document: "readonly",
        window: "readonly",
        fetch: "readonly",
        FormData: "readonly",
        Event: "readonly",
        console: "readonly",
      },
    },
    rules: {
      "no-undef": "error",
      "no-unused-vars": "warn",
      eqeqeq: "error",
      "no-console": "off",
      semi: ["warn", "always"],
    },
  },
];