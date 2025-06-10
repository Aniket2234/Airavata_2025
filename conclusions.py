import random

def clean_value(value):
    """Cleans the input value by removing units and converting to float if possible."""
    try:
        return float(value.split()[0])  # Split by space and take the first part
    except (ValueError, IndexError):
        return None  # Return None if conversion fails

def generate_conclusions(results):
    """Generates conclusions for each element based on simulation results."""
    conclusions = []
    
    # Define multiple conclusions for each element class
    conclusions_dict = {
        "InletReservoir": [
            "Inlet reservoir level is low.",
            "Inlet reservoir level is sufficient.",
            "Inlet reservoir flow rate is critically low, check for blockages.",
            "Inlet reservoir is full and may overflow."
        ],
        "OutletReservoir": [
            "Outlet reservoir level is low.",
            "Outlet reservoir is ready to receive flow.",
            "Outlet reservoir is under heavy demand.",
            "Outlet reservoir level is stable."
        ],
        "Valve": [
            "Valve is functioning normally.",
            "Valve head loss is high.",
            "Valve is closed.",
            "Valve is partially open.",
            "Valve is efficient with minimal head loss."
        ],
        "Manifold": [
            "Manifold is distributing flow effectively.",
            "Manifold elevation is low.",
            "Manifold may need adjustment due to uneven flow."
        ],
        "SurgeTank": [
            "Surge tank is stabilizing flow.",
            "Surge tank is experiencing low stability.",
            "Surge tank is not stabilizing effectively due to flow fluctuations."
        ],
        "Turbine": [
            "Turbine output is low.",
            "Turbine output is optimal.",
            "Turbine may require maintenance due to low efficiency."
        ],
        "Pipe": [
            "Pipe flow rate is low.",
            "Pipe flow rate is optimal.",
            "Pipe may have excessive friction losses due to length."
        ]
    }

    for result in results:
        element_name, element_class, result_value, flow_rate, head_loss, energy_output, flow_conclusion, _ = result
        
        # Clean the values
        cleaned_result_value = clean_value(result_value)
        cleaned_flow_rate = clean_value(flow_rate)
        cleaned_head_loss = clean_value(head_loss)
        cleaned_energy_output = clean_value(energy_output)

        if element_class in conclusions_dict:
            # Select conclusion based on specific conditions
            if element_class == "InletReservoir":
                if cleaned_result_value is not None and cleaned_result_value < 1.0:
                    conclusion_template = conclusions_dict[element_class][0]  # Low level
                elif cleaned_flow_rate is not None and cleaned_flow_rate < 0.1:
                    conclusion_template = conclusions_dict[element_class][2]  # Critically low flow rate
                elif cleaned_result_value is not None and cleaned_result_value >= 10.0:  # Assuming 10.0 is max capacity
                    conclusion_template = conclusions_dict[element_class][3]  # Full reservoir
                else:
                    conclusion_template = random.choice(conclusions_dict[element_class])
            elif element_class == "OutletReservoir":
                if cleaned_result_value is not None and cleaned_result_value < 1.0:
                    conclusion_template = conclusions_dict[element_class][0]  # Low level
                elif cleaned_flow_rate is not None and cleaned_flow_rate > 5.0:
                    conclusion_template = conclusions_dict[element_class][2]  # Heavy demand
                else:
                    conclusion_template = random.choice(conclusions_dict[element_class])
            elif element_class == "Valve":
                if cleaned_head_loss is not None and cleaned_head_loss > 5.0:
                    conclusion_template = conclusions_dict[element_class][1]  # High head loss
                elif cleaned_flow_rate is not None and cleaned_flow_rate == 0:
                    conclusion_template = conclusions_dict[element_class][2]  # Valve closed
                elif cleaned_head_loss is not None and cleaned_head_loss < 1.0:
                    conclusion_template = conclusions_dict[element_class][4]  # Efficient valve
                else:
                    conclusion_template = random.choice(conclusions_dict[element_class])
            elif element_class == "Manifold":
                if cleaned_result_value is not None and cleaned_result_value < 1.0:
                    conclusion_template = conclusions_dict[element_class][1]  # Low elevation
                elif cleaned_flow_rate is not None and cleaned_flow_rate < 1.0:  # Example condition
                    conclusion_template = conclusions_dict[element_class][2]  # Uneven flow
                else:
                    conclusion_template = random.choice(conclusions_dict[element_class])
            elif element_class == "SurgeTank":
                if cleaned_flow_rate is not None and (cleaned_flow_rate < 0.5 or cleaned_flow_rate > 5.0):  # Example condition for fluctuation
                    conclusion_template = conclusions_dict[element_class][2]  # Low stability
                else:
                    conclusion_template = random.choice(conclusions_dict[element_class])
            elif element_class == "Turbine":
                if cleaned_energy_output is not None and cleaned_energy_output < 10.0:
                    conclusion_template = conclusions_dict[element_class][0]  # Low output
                elif cleaned_energy_output is not None and cleaned_energy_output > 100.0:  # Example threshold for optimal output
                    conclusion_template = conclusions_dict[element_class][1]  # Optimal output
                else:
                    conclusion_template = random.choice(conclusions_dict[element_class])
            elif element_class == "Pipe":
                if cleaned_flow_rate is not None and cleaned_flow_rate < 0.5:
                    conclusion_template = conclusions_dict[element_class][0]  # Low flow rate
                elif cleaned_flow_rate is not None and cleaned_flow_rate > 5.0:  # Example condition for high flow
                    conclusion_template = "Pipe flow rate is high, check for potential cavitation."
                else:
                    conclusion_template = random.choice(conclusions_dict[element_class])
            conclusions.append(conclusion_template.format(result_value=result_value, head_loss=head_loss, energy_output=energy_output, flow_rate=flow_rate))

    return conclusions

def generate_final_conclusion(results):
    """Generates a final conclusion based on the overall simulation results."""
    total_energy_output = 0
    total_flow_rate = 0
    total_head_loss = 0
    num_elements = len(results)
    optimal_flow_rate_count = 0
    high_head_loss_count = 0

    for result in results:
        element_name, element_class, result_value, flow_rate, head_loss, energy_output, flow_conclusion, _ = result
        
        # Accumulate energy output
        cleaned_energy_output = clean_value(energy_output)
        if cleaned_energy_output is not None:
            total_energy_output += cleaned_energy_output

        # Accumulate flow rate
        cleaned_flow_rate = clean_value(flow_rate)
        if cleaned_flow_rate is not None:
            total_flow_rate += cleaned_flow_rate

        # Accumulate head loss
        cleaned_head_loss = clean_value(head_loss)
        if cleaned_head_loss is not None:
            total_head_loss += cleaned_head_loss

        # Count optimal flow rates and high head losses
        if cleaned_flow_rate is not None and cleaned_flow_rate >= 0.5:
            optimal_flow_rate_count += 1
        if cleaned_head_loss is not None and cleaned_head_loss > 5.0:
            high_head_loss_count += 1

    # Generate final conclusion based on accumulated data
    if num_elements > 0:
        average_energy_output = total_energy_output / num_elements
        average_flow_rate = total_flow_rate / num_elements
        average_head_loss = total_head_loss / num_elements

        final_conclusion = (
            f"Overall, the average energy output is {average_energy_output:.2f} kW, "
            f"the average flow rate is {average_flow_rate:.2f} m³/s, "
            f"and the average head loss is {average_head_loss:.2f} m. "
        )

        if optimal_flow_rate_count == num_elements:
            final_conclusion += "All elements are operating at optimal flow rates."
        if high_head_loss_count > 0:
            final_conclusion += f"There are {high_head_loss_count} elements with high head loss."

    return final_conclusion.strip() 