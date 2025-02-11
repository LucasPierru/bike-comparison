import Image from "next/image";
import { ExternalLink, Tag } from "lucide-react";
import { Bike } from "@/types/bike.types";
import Link from "next/link";

interface BikeCardProps {
  bike: Bike;
}

export function BikeCard({ bike }: BikeCardProps) {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow">
      <div className="relative w-full h-64">
        <Image
          src={bike.imageUrl}
          alt={`${bike.brand.name} ${bike.name}`}
          fill
          className="w-full h-full object-cover absolute"
        />
        {/* {bike.salePrice && (
          <div className="absolute top-4 right-4 bg-red-500 text-white px-3 py-1 rounded-full">
            {discount}% OFF
          </div>
        )} */}
      </div>

      <div className="p-4">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold">{bike.brand.name}</h3>
          <span className="text-sm px-2 py-1 bg-gray-100 rounded-full">
            {bike.type}
          </span>
        </div>
        <p className="text-gray-600 mb-2">{bike.name}</p>

        {/* <div className="flex items-center gap-2 mb-4">
          {bike.salePrice ? (
            <>
              <span className="text-xl font-bold text-red-500">
                ${bike.salePrice}
              </span>
              <span className="text-gray-400 line-through">${bike.price}</span>
            </>
          ) : (
            <span className="text-xl font-bold">${bike.price}</span>
          )}
        </div> */}
        <div className="flex items-center gap-2 mb-4">
          <span className="text-xl font-bold">${bike.currentPrice}</span>
        </div>

        {/* <div className="space-y-2 mb-4">
          <p className="text-sm text-gray-600">Frame: {bike.specs.frame}</p>
          <p className="text-sm text-gray-600">
            Groupset: {bike.specs.groupset}
          </p>
          <p className="text-sm text-gray-600">
            Wheel Size: {bike.specs.wheelSize}
          </p>
          {bike.specs.weight && (
            <p className="text-sm text-gray-600">Weight: {bike.specs.weight}</p>
          )}
        </div> */}

        <Link
          href={bike.affiliateLink.base_url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center justify-center w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          View Deal <ExternalLink className="ml-2 h-4 w-4" />
        </Link>
      </div>
    </div>
  );
}
