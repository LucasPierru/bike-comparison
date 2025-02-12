import Link from "next/link";
import RangeFilter from "./range-filter/range-filter";

export type BikeType = {
  name: string;
  value: string;
};

interface FiltersProps {
  types: BikeType[];
  selectedType: string;
  priceRange: [number, number];
}

export function Filters({ types, selectedType, priceRange }: FiltersProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-semibold mb-3">Category</h3>
          <div className="flex flex-wrap gap-2">
            {types.map((type) => (
              <Link
                key={type.value}
                href={`/?type=${type.value}`}
                className={`px-4 py-2 rounded-full text-sm ${
                  selectedType === type.value
                    ? "bg-blue-600 text-white"
                    : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                }`}
              >
                {type.name}
              </Link>
            ))}
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold mb-3">Price Range</h3>
          <div className="space-y-2">
            <div className="flex justify-between text-sm text-gray-600">
              <span>${priceRange[0]}</span>
              <span>${priceRange[1]}</span>
            </div>
            <RangeFilter currentValue={priceRange[1]} />
          </div>
        </div>
      </div>
    </div>
  );
}
