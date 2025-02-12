"use client";

import { useRouter } from "next/navigation";
import { ChangeEvent } from "react";

type RangeFilterProps = {
  currentValue: number;
};

export function RangeFilter({ currentValue }: RangeFilterProps) {
  const router = useRouter();

  const updateRange = (event: ChangeEvent<HTMLInputElement>) => {
    router.push(`/?maxPrice=${event.target.value}`);
  };

  return (
    <input
      type="range"
      min="0"
      max="20000"
      step="100"
      value={currentValue}
      onChange={updateRange}
      className="w-full"
    />
  );
}

export default RangeFilter;
