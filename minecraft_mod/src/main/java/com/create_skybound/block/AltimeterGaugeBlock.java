package com.create_skybound.block;

import net.minecraft.core.BlockPos;
import net.minecraft.core.Direction;
import net.minecraft.network.chat.Component;
import net.minecraft.util.Mth;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.ItemInteractionResult;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.context.BlockPlaceContext;
import net.minecraft.world.level.BlockGetter;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.RenderShape;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.StateDefinition;
import net.minecraft.world.level.block.state.properties.BlockStateProperties;
import net.minecraft.world.level.block.state.properties.DirectionProperty;
import net.minecraft.world.level.block.state.properties.IntegerProperty;
import net.minecraft.world.phys.BlockHitResult;
import net.minecraft.world.phys.shapes.CollisionContext;
import net.minecraft.world.phys.shapes.VoxelShape;
import org.jetbrains.annotations.Nullable;

public class AltimeterGaugeBlock extends Block {
    public static final DirectionProperty FACING = BlockStateProperties.HORIZONTAL_FACING;
    public static final IntegerProperty LEVEL_OUTPUT = IntegerProperty.create("level_output", 0, 15);

    private static final VoxelShape SHAPE_NORTH = Block.box(3.0, 3.0, 14.0, 13.0, 13.0, 16.0);
    private static final VoxelShape SHAPE_SOUTH = Block.box(3.0, 3.0, 0.0, 13.0, 13.0, 2.0);
    private static final VoxelShape SHAPE_WEST = Block.box(14.0, 3.0, 3.0, 16.0, 13.0, 13.0);
    private static final VoxelShape SHAPE_EAST = Block.box(0.0, 3.0, 3.0, 2.0, 13.0, 13.0);

    public AltimeterGaugeBlock(Properties properties) {
        super(properties);
        this.registerDefaultState(this.stateDefinition.any()
                .setValue(FACING, Direction.NORTH)
                .setValue(LEVEL_OUTPUT, 0));
    }

    @Override
    protected void createBlockStateDefinition(StateDefinition.Builder<Block, BlockState> builder) {
        builder.add(FACING, LEVEL_OUTPUT);
    }

    @Nullable
    @Override
    public BlockState getStateForPlacement(BlockPlaceContext context) {
        Direction dir = context.getHorizontalDirection().getOpposite();
        int output = calculateSignal(context.getClickedPos().getY());
        return this.defaultBlockState().setValue(FACING, dir).setValue(LEVEL_OUTPUT, output);
    }

    @Override
    protected VoxelShape getShape(BlockState state, BlockGetter level, BlockPos pos, CollisionContext context) {
        return switch (state.getValue(FACING)) {
            case SOUTH -> SHAPE_SOUTH;
            case WEST -> SHAPE_WEST;
            case EAST -> SHAPE_EAST;
            default -> SHAPE_NORTH;
        };
    }

    @Override
    protected RenderShape getRenderShape(BlockState state) {
        return RenderShape.MODEL;
    }

    @Override
    protected ItemInteractionResult useItemOn(ItemStack stack, BlockState state, Level level, BlockPos pos, Player player, InteractionHand hand, BlockHitResult hitResult) {
        if (!level.isClientSide) {
            int y = pos.getY();
            int seaLevelDiff = y - level.getSeaLevel();
            String prefix = seaLevelDiff >= 0 ? "+" : "";
            player.displayClientMessage(Component.translatable("message.create_skybound.altimeter_readout", y, prefix + seaLevelDiff), true);
        }
        return ItemInteractionResult.SUCCESS;
    }

    public static int calculateSignal(int y) {
        // -64 to 320 range (384 blocks)
        float clamped = Mth.clamp(y + 64, 0, 384);
        return Math.min(15, (int) ((clamped / 384.0f) * 15.0f));
    }

    @Override
    protected boolean hasAnalogOutputSignal(BlockState state) {
        return true;
    }

    @Override
    protected int getAnalogOutputSignal(BlockState state, Level level, BlockPos pos) {
        return calculateSignal(pos.getY());
    }
}
