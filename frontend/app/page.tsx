import { getBikes, getBikeTypes } from "@/requests/bike";
import { BikeCard } from "@/components/bike-card/bike-card";
import { getTypeNameFromSlug } from "@/lib/utils";
import { Filters } from "@/components/filters/filters";

export default async function Home({
  searchParams,
}: {
  searchParams: { type: string; minPrice: number; maxPrice: number };
}) {
  const { type, minPrice, maxPrice } = await searchParams;

  const { bikes } = await getBikes(type);
  const { bikeTypes } = await getBikeTypes();

  const types = bikeTypes!.map((type) => ({
    name: getTypeNameFromSlug(type),
    value: type,
  }));

  return (
    <div className="min-h-screen p-8 pb-20 sm:p-20">
      <main className="grid grid-cols-4 gap-8 row-start-2 items-center sm:items-start">
        <div className="col-span-full">
          <Filters
            types={types}
            selectedType={type}
            priceRange={[minPrice, maxPrice]}
          />
        </div>
        {bikes && bikes.map((bike) => <BikeCard key={bike._id} bike={bike} />)}
      </main>
    </div>
  );
}
