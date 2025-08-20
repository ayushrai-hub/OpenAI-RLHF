#include <netcdf>
#include <vector>
#include <string>
#include <cmath>
#include <algorithm>
#include <memory>

class EnvironmentManager {
public:
    void addDataset(const std::string& filename) {
        datasets.emplace_back(std::make_unique<netCDF::NcFile>(filename, netCDF::NcFile::read));
    }

    double getValue(double timeVal, double depthVal, double latVal, double lonVal) {
        double sum = 0.0;
        size_t count = 0;
        for(auto& ptr : datasets) {
            // LTC: get the variables: time, depth, lat, lon, data
            netCDF::NcFile& file = *ptr;
            netCDF::NcVar timeVar = file.getVar("time");
            netCDF::NcVar depthVar = file.getVar("depth");
            netCDF::NcVar latVar = file.getVar("lat");
            netCDF::NcVar lonVar = file.getVar("lon");
            netCDF::NcVar dataVar = file.getVar("data");
            if(timeVar.isNull() || depthVar.isNull() || latVar.isNull() || lonVar.isNull() || dataVar.isNull()) {
                continue; // skip dataset if variable not found
            }
            // Get coordinate arrays
            std::vector<double> timeArr(timeVar.getDim(0).getSize());
            std::vector<double> depthArr(depthVar.getDim(0).getSize());
            std::vector<double> latArr(latVar.getDim(0).getSize());
            std::vector<double> lonArr(lonVar.getDim(0).getSize());
            timeVar.getVar(timeArr.data());
            depthVar.getVar(depthArr.data());
            latVar.getVar(latArr.data());
            lonVar.getVar(lonArr.data());
            // Check boundaries
            if(timeVal < timeArr.front() || timeVal > timeArr.back() ||
               depthVal < depthArr.front() || depthVal > depthArr.back() ||
               latVal < latArr.front() || latVal > latArr.back() ||
               lonVal < lonArr.front() || lonVal > lonArr.back()) {
                // Out of range for this dataset, skip
                continue;
            }
            // Find nearest indices
            auto findIndex = [](const std::vector<double>& arr, double val)->size_t{
                auto it = std::lower_bound(arr.begin(), arr.end(), val);
                if(it == arr.end()) return arr.size()-1;
                if(it == arr.begin()) return 0;
                // determine nearest
                if(val - *(it-1) <= *it - val) return (it-1) - arr.begin();
                return it - arr.begin();
            };
            size_t timeIndex  = findIndex(timeArr, timeVal);
            size_t depthIndex = findIndex(depthArr, depthVal);
            size_t latIndex   = findIndex(latArr, latVal);
            size_t lonIndex   = findIndex(lonArr, lonVal);
            // Get data at indices
            float val;
            std::vector<size_t> start{timeIndex, depthIndex, latIndex, lonIndex};
            std::vector<size_t> countArr{1,1,1,1};
            dataVar.getVar(start, countArr, &val);
            sum += val;
            count++;
        }
        if(count == 0) {
            return std::nan("");
        }
        return sum / count;
    }
private:
    std::vector<std::unique_ptr<netCDF::NcFile>> datasets;
};

int main(){
    // Example usage; actual unit tests will create EnvironmentManager and use addDataset and getValue.
}
