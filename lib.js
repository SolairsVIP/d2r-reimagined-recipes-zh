(function (root) {
  'use strict';

  function normalize(value) {
    return String(value || '').normalize('NFKC').toLowerCase().trim();
  }

  function findRecipes(recipes, options = {}) {
    const words = normalize(options.query).split(/\s+/).filter(Boolean);
    return recipes.filter((recipe) => {
      if (options.group && options.group !== '全部' && recipe.group !== options.group) return false;
      if (options.section && options.section !== '全部' && recipe.section !== options.section) return false;
      const text = normalize([recipe.group, recipe.section, ...recipe.inputs, recipe.output].join(' '));
      return words.every((word) => text.includes(word));
    });
  }

  const api = { findRecipes };
  if (typeof module !== 'undefined' && module.exports) module.exports = api;
  if (root) root.RecipeSearch = api;
})(typeof window !== 'undefined' ? window : null);
