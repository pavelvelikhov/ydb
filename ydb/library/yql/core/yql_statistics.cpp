#include <util/generic/yexception.h>
#include "yql_statistics.h"

#include <library/cpp/json/json_reader.h>


using namespace NYql;

static TString ConvertToStatisticsTypeString(EStatisticsType type) {
    switch (type) {
        case EStatisticsType::BaseTable:
            return "BaseTable";
        case EStatisticsType::FilteredFactTable:
            return "FilteredFactTable";
        case EStatisticsType::ManyManyJoin:
            return "ManyManyJoin";
        default:
            Y_ENSURE(false,"Unknown EStatisticsType");
    }
    return "";
}

std::ostream& NYql::operator<<(std::ostream& os, const TOptimizerStatistics& s) {
    os << "Type: " << ConvertToStatisticsTypeString(s.Type) << ", Nrows: " << s.Nrows
        << ", Ncols: " << s.Ncols << ", ByteSize: " << s.ByteSize << ", Cost: " << s.Cost;
    for (const auto& c : s.KeyColumns) {
        os << ", " << c;
    }
    return os;
}

bool TOptimizerStatistics::Empty() const {
    return ! (Nrows || Ncols || Cost);
}

TOptimizerStatistics::TOptimizerStatistics(
    EStatisticsType type,
    double nrows,
    int ncols,
    double byteSize,
    double cost,
    const TVector<TString>& keyColumns,
    std::unique_ptr<IProviderStatistics> specific)
    : Type(type)
    , Nrows(nrows)
    , Ncols(ncols)
    , ByteSize(byteSize)
    , Cost(cost)
    , KeyColumns(keyColumns)
    , Specific(std::move(specific))
{
}

TOptimizerStatistics& TOptimizerStatistics::operator+=(const TOptimizerStatistics& other) {
    Nrows += other.Nrows;
    Ncols += other.Ncols;
    ByteSize += other.ByteSize;
    Cost += other.Cost;
    return *this;
}

const TVector<TString>& TOptimizerStatistics::EmptyColumns = TVector<TString>();

std::shared_ptr<TOptimizerStatistics> NYql::UpdateStatsWithHints(const NYql::TOptimizerStatistics& s, const TString& statHints) {
    TOptimizerStatistics* res = new TOptimizerStatistics(s.Type, s.Nrows, s.Ncols, s.ByteSize);

    NJson::TJsonValue root;
    NJson::ReadJsonTree(statHints, &root, true);
    auto tableStats = root.GetMapSafe();

    if (tableStats.contains("n_rows")) {
        res->Nrows = tableStats.at("n_rows").GetDoubleSafe();
    }
    if (tableStats.contains("byte_size")) {
        res->ByteSize = tableStats.at("byte_size").GetDoubleSafe();
    }
    if (tableStats.contains("n_attrs")) {
        res->Ncols = tableStats.at("n_attrs").GetIntegerSafe();
    }

    if (tableStats.contains("columns")) {
        res->ColumnStatistics = std::make_shared<THashMap<TString, TColumnStatistics>>();

        for (auto col : tableStats.at("columns").GetArraySafe()) {
            auto colMap = col.GetMapSafe();

            TColumnStatistics cStat;

            auto column_name = colMap.at("name").GetStringSafe();

            if (colMap.contains("n_unique_vals")) {
                cStat.NuniqueVals = colMap.at("n_unique_vals").GetDoubleSafe();
            }
            if (colMap.contains("hyperloglog")) {
                cStat.HyperLogLog = colMap.at("hyperloglog").GetDoubleSafe();
            }

            (*res->ColumnStatistics)[column_name] = cStat;
        }
    }

    return std::shared_ptr<TOptimizerStatistics>(res);
}

