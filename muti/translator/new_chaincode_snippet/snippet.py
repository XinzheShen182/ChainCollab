import json

with open("new_chaincode_snippet/snippet.json", "r") as f:
    content = json.load(f)


def import_code(
    if_oracle: bool = False,
    if_stateCharts: bool = False,
):
    extra_imports = ""
    if if_oracle:
        extra_imports += content["OracleImport"] + "\n"
    if if_stateCharts:
        extra_imports += "\t" + content["StateChartsImport"] + "\n"
    return content["importFrame"].format(extra_imports=extra_imports)


def contract_definition_code():
    return content["contract_definition"]


def fix_part_code():
    return content["fix_part"]


def package_code():
    return content["package"]


def state_read_and_put_code():
    return content["StateReadAndSetFunc"]


def globale_variable_read_and_set_code():
    return content["ReadAndSetGloablVariable"]


def CreateInstance_code(
    start_event: str,
    end_events: list[str],
    choreography_tasks: list[dict[str, str]],
    messages: list[dict[str, str]],
    gateways: list,
    participants: list,
    business_rules: list,
):
    def InitMessage(message: str, sender: str, receiver: str, is_multi: str, properties: str, choreography_task: str) -> str:
        return content["InitMessageFrame"].format(
            message=message, sender=sender, receiver=receiver, format=properties, is_multi=is_multi, choreographyTask=choreography_task
        )

    def InitParticipant(
        participant: str,
        is_multi: bool,
        multi_maximum: int,
        multi_minimum: int,
    ) -> str:
        """cc.CreateParticipant(ctx, "Participant_1gcdqza", "Org1MSP", map[string]string{"role": "customer"}, is_multi, multi_maximum, multi_minimum)"""

        return content["InitParticipantFrame"].format(
            participant_id=participant,
            # is_multi=is_multi,
            multi_maximum=multi_maximum,
            multi_minimum=multi_minimum,
        )

    def InitChoreographyTask(
        choreographyTask: str, is_multi: bool, multi_type: str, init_message: str, response_message: str
    ) -> str:
        return content["InitChoreographyTaskFrame"].format(
            choreographyTask=choreographyTask,
            is_multi=is_multi,
            multi_type=multi_type,
            init_message=init_message,
            response_message=response_message,
        )

    def InitBusinessRule(business_rule: str) -> str:
        return content["InitBusinessRuleFrame"].format(business_rule=business_rule)

    return content["CreateInstanceFuncFrame"].format(
        create_elements_code="\n".join(
            [
                InitParticipant(
                    participant["id"],
                    participant["is_multi"],
                    participant["multi_maximum"],
                    participant["multi_minimum"],
                )
                for participant in participants
            ]
            + [
                InitMessage(
                    message=message["id"],
                    sender=message["sender"],
                    receiver=message["receiver"],
                    is_multi=message["is_multi"],
                    properties=message["properties"],
                    choreography_task=message["choreography_task"],
                )
                for message in messages
            ]
            +[
                InitChoreographyTask(
                    choreographyTask=choreographyTask["id"],
                    is_multi=choreographyTask["is_multi"],
                    multi_type=choreographyTask["multi_type"],
                    init_message=choreographyTask["init_message"],
                    response_message=choreographyTask["response_message"],
                )
                for choreographyTask in choreography_tasks
            ]
        ),
        event_content="\n".join(
            [
                '"' + business_rule + '"' + " : " + f"initParameters.{business_rule}_Content,"
                for business_rule in business_rules
            ]
        ),
    )


def ChangeEventState_code(event, state: str):
    return content["ChangeEventStateFrame"].format(event=event, state=state)


def ChangeMsgState_code(msg, state: str):
    return content["ChangeMsgStateFrame"].format(message=msg, state=state)


def ChangeGtwState_code(gtw, state: str):
    return content["ChangeGtwStateFrame"].format(gateway=gtw, state=state)


def ChangeBusinessRuleState_code(business_rule, state: str):
    return content["ChangeBusinessRuleStateFrame"].format(business_rule=business_rule, state=state)


def StartEvent_code(
    event,
    change_next_state_code: str,
    pre_activate_next_hook: str = "",
    after_all_hook: str = "",
):
    return content["StartEventFuncFrame"].format(
        event=event,
        change_next_state_code=change_next_state_code,
        pre_activate_next_hook=pre_activate_next_hook,
        after_all_hook=after_all_hook,
    )


def EndEvent_code(event, after_all_hook: str = ""):
    return content["EndEventFuncFrame"].format(
        event=event,
        after_all_hook=after_all_hook,
    )


def MessageSend_code(
    message,
    after_all_hook: str = "",
    more_parameters: str = "",
    put_more_parameters: str = "",
    put_more_event_parameters: str = "",
    change_self_state: str = "",
    key: str = "0",
):
    return content["MessageSendFuncFrame"].format(
        message=message,
        after_all_hook=after_all_hook,
        more_parameters=more_parameters,
        put_more_parameters=put_more_parameters,
        put_more_event_parameters=put_more_event_parameters,
        change_self_state=change_self_state,
        msg_key=f"{message}_{key}",
    )


def MessageAdvance_code(message):
    return content["MessageAdvanceFuncFrame"].format(message=message)


def MessageComplete_code(
    message,
    change_next_state_code: str = "",
    pre_activate_next_hook: str = "",
    after_all_hook: str = "",
):
    return content["MessageCompleteFuncFrame"].format(
        message=message
    )


# TODO
def ExclusiveGateway_split_code(
    gateway,
    change_next_state_code: str,
    pre_activate_next_hook: str = "",
    after_all_hook: str = "",
):
    return content["ExclusiveGatewaySplitFuncFrame"].format(
        exclusive_gateway=gateway,
        change_next_state_code=change_next_state_code,
        pre_activate_next_hook=pre_activate_next_hook,
        after_all_hook=after_all_hook,
    )


def ExclusiveGateway_merge_code(
    gateway,
    change_next_state_code,
    pre_activate_next_hook: str = "",
    after_all_hook: str = "",
):
    return content["ExclusiveGatewayMergeFuncFrame"].format(
        exclusive_gateway=gateway,
        change_next_state_code=change_next_state_code,
        pre_activate_next_hook=pre_activate_next_hook,
        after_all_hook=after_all_hook,
    )


def ParallelGateway_split_code(
    gateway,
    change_next_state_code: str,
    pre_activate_next_hook: str = "",
    after_all_hook: str = "",
):
    return content["ParallelGatewaySplitFuncFrame"].format(
        parallel_gateway=gateway,
        change_next_state_code=change_next_state_code,
        pre_activate_next_hook=pre_activate_next_hook,
        after_all_hook=after_all_hook,
    )


def ParallelGateway_merge_code(
    gateway,
    change_next_state_code: str,
    pre_activate_next_hook: str = "",
    after_all_hook: str = "",
):
    return content["ParallelGatewayMergeFuncFrame"].format(
        parallel_gateway=gateway,
        change_next_state_code=change_next_state_code,
        pre_activate_next_hook=pre_activate_next_hook,
        after_all_hook=after_all_hook,
    )


def EventBasedGateway_code(
    gateway,
    change_next_state_code: str,
    pre_activate_next_hook: str = "",
    after_all_hook: str = "",
):
    return content["EventBasedGatewayFuncFrame"].format(
        event_based_gateway=gateway,
        change_next_state_code=change_next_state_code,
        pre_activate_next_hook=pre_activate_next_hook,
        after_all_hook=after_all_hook,
    )


## Conditions
##----------------


def CheckMessageState_code(message, state: str):
    return content["CheckMessageStateFrame"].format(state=state, message=message)


def CheckGatewayState_code(gateway, state: str):
    return content["CheckGtwStateFrame"].format(state=state, gateway=gateway)


def CheckEventState_code(event, state: str):
    return content["CheckEventStateFrame"].format(state=state, event=event)


##----------------


## Combine Conditions
##----------------
def CombineConditions_All_True_code(conditions: list[str]):
    return "&&".join(conditions)


def CombineConditions_Any_False_code(conditions: list[str]):
    return "||".join([f"!({condition})" for condition in conditions])


def CombineConditions_Any_True_code(conditions: list[str]):
    return "||".join(conditions)


def CombineConditions_All_False_code(conditions: list[str]):
    return "&&".join([f"!({condition})" for condition in conditions])


##----------------

## Condition Behaviour
##----------------


def ConditionToDo_code(condition: str, todo: str):
    return content["ConditionToDoFrame"].format(condition=condition, todo=todo)


def ConditionToHalt_code(condition: str):
    return ConditionToDo_code(condition, "return nil")


##----------------


def StateMemoryDefinition_code(fields: str):
    return content["StateMemoryDefinitionFrame"].format(fields=fields)


def StructParameterDefinition_code(name: str, type: str):
    # <name> bool `json:"<name>"`
    return '{name} {type} `json:"{name}"`'.format(name=name, type=type)


# deprecated
def PutState_code(name: str, value: str):
    return content["PutStateFuncFrame"].format(name=name, value=value)


def SetGlobalVariable_code(items: str = ""):
    return content["SetGlobalVariableFuncFrame"].format(items=items)


def SetGlobalVaribaleItem_code(name: str, value: str):
    return content["SetGlobalVaribaleFuncItemFrame"].format(name=name, value=value)


def ReadState_code(name: str):
    return content["ReadStateFuncFrame"].format(stateName=name)


@DeprecationWarning
def ReadCurrentMemory_code():
    return content["ReadCurrentMemoryCode"]


def ReadGlobalMemory_code():
    return content["ReadGlobalVariable"]


def InitParametersTypeDefFrame_code(fields: str):
    return content["InitParametersTypeDefFrame"].format(fields=fields)


def InitParametersDefinition_code(name: str, type: str):
    return '{name} {type} `json:"{name}"`'.format(name=name, type=type)


def RegisterFunc_code():
    return content["RegisterFunc"]


def CheckRegisterFunc_code():
    return content["CheckRegisterFunc"]


def BusinessRuleFuncFrame_code(
    business_rule: str,
    pre_activate_next_hook: str = "",
    after_all_hook: str = "",
    change_next_state_code: str = "",
):
    return content["BusinessRuleFuncFrame"].format(
        business_rule=business_rule,
        pre_activate_next_hook=pre_activate_next_hook,
        after_all_hook=after_all_hook,
        change_next_state_code=change_next_state_code,
    )


def BusinessRuleContinueFuncFrame_code(
    business_rule: str,
    pre_activate_next_hook: str = "",
    after_all_hook: str = "",
    change_next_state_code: str = "",
):
    return content["BusinessRuleContinueFuncFrame"].format(
        business_rule=business_rule,
        pre_activate_next_hook=pre_activate_next_hook,
        after_all_hook=after_all_hook,
        change_next_state_code=change_next_state_code,
    )


def InvokeChaincodeFunc_code():
    return content["InvokeChaincodeFunc"]


def Gateway_code(gateway):
    return content["GatewayFuncFrame"].format(gateway=gateway)


def Event_code(event):
    return content["EventFuncFrame"].format(event=event)
