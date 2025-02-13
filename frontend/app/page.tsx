import { getBikes, getBikeTypes } from "@/requests/bike";
import { BikeCard } from "@/components/bike-card/bike-card";
import { getTypeNameFromSlug } from "@/lib/utils";
import { Filters } from "@/components/filters/filters";

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  console.log({ params: await searchParams });
  const { type, minPrice, maxPrice } = await searchParams;

  const { bikes } = await getBikes(type as string);
  const { bikeTypes } = await getBikeTypes();

  const types = bikeTypes!.map((type) => ({
    name: getTypeNameFromSlug(type),
    value: type,
  }));

  const bikeType = type || "all";
  const min = Number(minPrice) || 0;
  const max = Number(maxPrice) || 20000;

  return (
    <div className="min-h-screen p-8 pb-20 sm:p-20">
      <main className="grid grid-cols-4 gap-8 row-start-2 items-center sm:items-start">
        <div className="col-span-full">
          <Filters
            types={types}
            selectedType={bikeType as string}
            priceRange={[min, max]}
          />
        </div>
        {bikes && bikes.map((bike) => <BikeCard key={bike._id} bike={bike} />)}
      </main>
    </div>
  );
}
