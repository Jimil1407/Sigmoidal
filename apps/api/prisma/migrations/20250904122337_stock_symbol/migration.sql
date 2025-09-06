/*
  Warnings:

  - You are about to drop the column `stockId` on the `Prediction` table. All the data in the column will be lost.
  - You are about to drop the column `stockId` on the `Trade` table. All the data in the column will be lost.
  - You are about to drop the column `stockId` on the `Watchlist` table. All the data in the column will be lost.
  - Added the required column `stockSymbol` to the `Prediction` table without a default value. This is not possible if the table is not empty.
  - Added the required column `stockSymbol` to the `Trade` table without a default value. This is not possible if the table is not empty.
  - Added the required column `stockSymbol` to the `Watchlist` table without a default value. This is not possible if the table is not empty.

*/
-- DropForeignKey
ALTER TABLE "Prediction" DROP CONSTRAINT "Prediction_stockId_fkey";

-- DropForeignKey
ALTER TABLE "Trade" DROP CONSTRAINT "Trade_stockId_fkey";

-- DropForeignKey
ALTER TABLE "Watchlist" DROP CONSTRAINT "Watchlist_stockId_fkey";

-- AlterTable
ALTER TABLE "Prediction" DROP COLUMN "stockId",
ADD COLUMN     "stockSymbol" TEXT NOT NULL;

-- AlterTable
ALTER TABLE "Trade" DROP COLUMN "stockId",
ADD COLUMN     "stockSymbol" TEXT NOT NULL;

-- AlterTable
ALTER TABLE "Watchlist" DROP COLUMN "stockId",
ADD COLUMN     "stockSymbol" TEXT NOT NULL;

-- AddForeignKey
ALTER TABLE "Trade" ADD CONSTRAINT "Trade_stockSymbol_fkey" FOREIGN KEY ("stockSymbol") REFERENCES "Stock"("symbol") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Prediction" ADD CONSTRAINT "Prediction_stockSymbol_fkey" FOREIGN KEY ("stockSymbol") REFERENCES "Stock"("symbol") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Watchlist" ADD CONSTRAINT "Watchlist_stockSymbol_fkey" FOREIGN KEY ("stockSymbol") REFERENCES "Stock"("symbol") ON DELETE RESTRICT ON UPDATE CASCADE;
