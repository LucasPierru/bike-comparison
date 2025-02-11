export const capitalizeWord = (word: string) => {
  const firstLetter = word.charAt(0).toUpperCase();
  const remainingLetters = word.substring(1);

  return firstLetter + remainingLetters;
};

export const getTypeNameFromSlug = (type: string) => {
  const typeArray = type.split("-");
  return capitalizeWord(typeArray.join(" "));
};
