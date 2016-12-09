//auto-includes a line separator in case you don't; this line separator will be '\n' since the CG servers linux
//also auto-trims leading and trailing whitespace in a file (thus omitting files whose contents are made empty by include guards entirely)
class auto_detects_header_src_pairs {};
void auto_detects_header_src_pairs_fn() {}
class can_import_targets_within_directory_paths {};
class can_import_targets_in_both_parent_and_child_directories {};
void can_import_targets_within_directory_paths() {}
class supports_pragma_once {};
class handles_both_ifdef_and_ifndef_for_include_guards {};
#if 1
    class ignores_and_reprints_other_ifs_a{};
#elif 1
    class ignores_and_reprints_other_ifs_b{};
#else
    class ignores_and_reprints_other_ifs_c{};
#endif
class can_deal_with_nested_ifs {};
//only processes local includes
#include <string>
//only processes local includes
#include <iostream>
#ifndef ONLY_PROCESSES_PREFIXED_INCLUDE_GUARDS
#define ONLY_PROCESSES_PREFIXED_INCLUDE_GUARDS
//only processes prefixed ifdefs/ifndefs
#endif //ONLY_PROCESSES_PREFIXED_INCLUDE_GUARDS
struct can_detect_both_c_and_cpp_files {};
void can_detect_both_c_and_cpp_files() {}
//repeated includes are safely omitted when #pragma once or appropriately prefixed include guards are present
int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}