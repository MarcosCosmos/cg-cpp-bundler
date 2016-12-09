#include "auto_includes_a_line_seperator_between_files_incase_you_dont.hpp"
#include "auto_detects_header_src_pairs.hpp"
#include "subfolder/can_import_targets_within_directories.hpp"
#include "supports_pramga_once.hpp"
#include "handles_both_ifdef_and_ifndef_for_include_guards.hpp"
#include "ignores_and_reprints_other_ifs.hpp"
#include "can_deal_with_nested_ifs.hpp"
#include "only_processes_local_includes.hpp"
#include "only_processes_prefixed_include_guards.hpp"
#include "can_detect_both_c_and_cpp_files.h"
//repeated includes are safely omitted when #pragma once or appropriately prefixed include guards are present
#include "auto_detects_header_src_pairs.hpp"
#include "supports_pramga_once.hpp"
int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}